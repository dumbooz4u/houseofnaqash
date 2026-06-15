<?php
/**
 * House of Naqash — catalogue manager.
 *
 * Products and categories live in data/products.json; the site renders from
 * that file, so every change here is live immediately.
 *
 * To change the password: run
 *   php -r 'echo password_hash("your-new-password", PASSWORD_DEFAULT), PHP_EOL;'
 * and paste the result into PASSWORD_HASH below.
 */

const PASSWORD_HASH = '$2y$12$FMighSNVBIk1WhiyVENpseP1A5lQAPX47niTnCRZFOsLgHZ/Cpm6K';

const DATA_FILE  = __DIR__ . '/data/products.json';
const IMAGES_DIR = __DIR__ . '/images';
const MAX_UPLOAD = 10 * 1024 * 1024; // 10 MB per image

// collections that have their own designed page; they cannot be deleted
const BUILTIN = ['cushions', 'fabrics', 'rugs', 'throws'];
// names that cannot be used as a new collection slug
const RESERVED = ['index', 'contact', 'collection', 'admin', 'images', 'css', 'js', 'data'];

const DEFAULT_COLLECTIONS = [
    ['slug' => 'cushions', 'label' => 'Cushions', 'grid' => 'square',
     'meta' => 'Hand-embroidered cushion',
     'subs' => [
         ['slug' => 'silk', 'label' => 'Silk',    'meta' => 'Silk · Hand embroidered'],
         ['slug' => 'wool', 'label' => 'Woollen', 'meta' => 'Wool · Crewel work'],
     ]],
    ['slug' => 'fabrics', 'label' => 'Fabrics', 'grid' => 'tall',
     'meta' => 'Crewel hand-embroidered cotton', 'subs' => []],
    ['slug' => 'rugs', 'label' => 'Rugs', 'grid' => 'rug',
     'meta' => 'Chain stitch rug', 'subs' => []],
    ['slug' => 'throws', 'label' => 'Throws', 'grid' => 'tall',
     'meta' => 'Throws & textiles', 'subs' => []],
];

session_start();

// ---------------------------------------------------------------- helpers --

function load_data(): array {
    $d = is_file(DATA_FILE) ? json_decode((string)file_get_contents(DATA_FILE), true) : [];
    if (empty($d['collections'])) $d['collections'] = DEFAULT_COLLECTIONS;
    $d['items'] = $d['items'] ?? [];
    return $d;
}

function save_data(array $data): void {
    $tmp = DATA_FILE . '.tmp';
    $json = json_encode(['collections' => array_values($data['collections']),
                         'items' => array_values($data['items'])],
        JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    if (file_put_contents($tmp, $json, LOCK_EX) === false || !rename($tmp, DATA_FILE)) {
        http_response_code(500);
        exit('Could not write data/products.json — check folder permissions.');
    }
    @chmod(DATA_FILE, 0664);
}

function slugify(string $s): string {
    $s = strtolower(trim($s));
    $s = preg_replace('/[^a-z0-9]+/', '-', $s);
    return trim($s, '-');
}

function find_collection(array $data, string $slug): ?array {
    foreach ($data['collections'] as $c) if ($c['slug'] === $slug) return $c;
    return null;
}

/** option value "coll:sub" (sub may be empty) -> [collection, sub|null], or null */
function resolve_category(array $data, string $value): ?array {
    [$cslug, $sslug] = array_pad(explode(':', $value, 2), 2, '');
    $coll = find_collection($data, $cslug);
    if (!$coll) return null;
    if ($sslug === '') return !empty($coll['subs']) ? null : [$coll, null];
    foreach ($coll['subs'] as $s) if ($s['slug'] === $sslug) return [$coll, $s];
    return null;
}

/** all selectable categories as value => label */
function category_options(array $data): array {
    $out = [];
    foreach ($data['collections'] as $c) {
        if (empty($c['subs'])) {
            $out[$c['slug'] . ':'] = $c['label'];
        } else {
            foreach ($c['subs'] as $s) {
                $out[$c['slug'] . ':' . $s['slug']] = $c['label'] . ' — ' . $s['label'];
            }
        }
    }
    return $out;
}

/** category value for an existing item ("coll:sub" or "coll:") */
function item_category(array $data, array $it): string {
    $coll = find_collection($data, $it['collection'] ?? '');
    if ($coll && !empty($coll['subs'])) {
        foreach ($coll['subs'] as $s) {
            if ($s['slug'] === ($it['cat'] ?? '')) return $coll['slug'] . ':' . $s['slug'];
        }
    }
    return ($it['collection'] ?? '') . ':';
}

function category_label(array $data, array $it): string {
    $opts = category_options($data);
    $key = item_category($data, $it);
    if (isset($opts[$key])) return $opts[$key];
    return ucfirst($it['collection'] ?? '?');
}

function image_in_use(string $file, array $items, ?string $except_id = null): bool {
    foreach ($items as $it) {
        if ($except_id !== null && $it['id'] === $except_id) continue;
        if (in_array($file, $it['images'], true)) return true;
    }
    return false;
}

function handle_uploads(string $title): array {
    $saved = [];
    if (empty($_FILES['photos'])) return $saved;
    $f = $_FILES['photos'];
    $count = is_array($f['name']) ? count($f['name']) : 0;
    for ($i = 0; $i < $count; $i++) {
        if ($f['error'][$i] === UPLOAD_ERR_NO_FILE) continue;
        if ($f['error'][$i] !== UPLOAD_ERR_OK) throw new RuntimeException('Upload failed for ' . $f['name'][$i]);
        if ($f['size'][$i] > MAX_UPLOAD) throw new RuntimeException($f['name'][$i] . ' is larger than 10 MB.');
        $info = @getimagesize($f['tmp_name'][$i]);
        $ext = match ($info['mime'] ?? '') {
            'image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp',
            default => null,
        };
        if ($ext === null) throw new RuntimeException($f['name'][$i] . ' is not a JPEG, PNG or WebP image.');
        $base = slugify($title) ?: 'item';
        $name = "$base.$ext";
        $n = 2;
        while (file_exists(IMAGES_DIR . "/$name")) { $name = "$base-$n.$ext"; $n++; }
        if (!move_uploaded_file($f['tmp_name'][$i], IMAGES_DIR . "/$name")) {
            throw new RuntimeException('Could not save ' . $f['name'][$i] . ' — check images/ permissions.');
        }
        @chmod(IMAGES_DIR . "/$name", 0664);
        $saved[] = $name;
    }
    return $saved;
}

function csrf_check(): void {
    if (!hash_equals($_SESSION['csrf'] ?? '', $_POST['csrf'] ?? '')) {
        http_response_code(403);
        exit('Session expired — go back and try again.');
    }
}

function e(string $s): string { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); }

// ------------------------------------------------------------------- auth --

if (($_GET['do'] ?? '') === 'logout') {
    session_destroy();
    header('Location: admin.php');
    exit;
}

$login_error = '';
if (($_POST['action'] ?? '') === 'login') {
    if (password_verify($_POST['password'] ?? '', PASSWORD_HASH)) {
        session_regenerate_id(true);
        $_SESSION['auth'] = true;
        $_SESSION['csrf'] = bin2hex(random_bytes(24));
        header('Location: admin.php');
        exit;
    }
    $login_error = 'That password is not correct.';
    sleep(1);
}

$authed = !empty($_SESSION['auth']);

// ---------------------------------------------------------------- actions --

$flash = '';
$error = '';
$data = load_data();

// one-time migration: persist the collections structure into the JSON
if ($authed && is_file(DATA_FILE)) {
    $raw = json_decode((string)file_get_contents(DATA_FILE), true);
    if (empty($raw['collections'])) save_data($data);
}

if ($authed && $_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') !== 'login') {
    csrf_check();
    try {
        switch ($_POST['action']) {
            case 'add':
                $title = trim($_POST['title'] ?? '');
                $cat = resolve_category($data, $_POST['category'] ?? '');
                if ($title === '' || !$cat) throw new RuntimeException('A title and category are required.');
                [$coll, $sub] = $cat;
                $images = handle_uploads($title);
                if (!$images) throw new RuntimeException('Please choose at least one photo.');
                $id = $coll['slug'] . '-' . slugify($title);
                $n = 2;
                while (array_filter($data['items'], fn($i) => $i['id'] === $id)) {
                    $id = $coll['slug'] . '-' . slugify($title) . "-$n"; $n++;
                }
                $data['items'][] = [
                    'id'         => $id,
                    'collection' => $coll['slug'],
                    'cat'        => $sub['slug'] ?? '',
                    'title'      => $title,
                    'meta'       => trim($_POST['meta'] ?? '') ?: ($sub['meta'] ?? '') ?: ($coll['meta'] ?? ''),
                    'desc'       => trim($_POST['desc'] ?? ''),
                    'images'     => $images,
                ];
                save_data($data);
                $flash = "“{$title}” added to " . ($sub ? "{$coll['label']} — {$sub['label']}" : $coll['label']) . '.';
                break;

            case 'edit':
                $id = $_POST['id'] ?? '';
                foreach ($data['items'] as $k => $it) {
                    if ($it['id'] !== $id) continue;
                    $title = trim($_POST['title'] ?? '') ?: $it['title'];
                    $cat = resolve_category($data, $_POST['category'] ?? '') ?? resolve_category($data, item_category($data, $it));
                    if (!$cat) throw new RuntimeException('Choose a valid category.');
                    [$coll, $sub] = $cat;
                    $data['items'][$k]['title'] = $title;
                    $data['items'][$k]['collection'] = $coll['slug'];
                    $data['items'][$k]['cat'] = $sub['slug'] ?? ($it['collection'] === $coll['slug'] && empty($coll['subs']) ? ($it['cat'] ?? '') : '');
                    $data['items'][$k]['meta'] = trim($_POST['meta'] ?? '') ?: ($sub['meta'] ?? '') ?: ($coll['meta'] ?? '');
                    $data['items'][$k]['desc'] = trim($_POST['desc'] ?? '');
                    $remove = $_POST['remove_images'] ?? [];
                    $kept = array_values(array_diff($it['images'], $remove));
                    $new = handle_uploads($title);
                    $final = array_merge($kept, $new);
                    if (!$final) throw new RuntimeException('A product needs at least one photo.');
                    $data['items'][$k]['images'] = $final;
                    save_data($data);
                    foreach ($remove as $file) {
                        if (!image_in_use($file, $data['items'])) @unlink(IMAGES_DIR . '/' . basename($file));
                    }
                    $flash = "“{$title}” updated.";
                    break;
                }
                break;

            case 'delete':
                $id = $_POST['id'] ?? '';
                foreach ($data['items'] as $k => $it) {
                    if ($it['id'] !== $id) continue;
                    unset($data['items'][$k]);
                    save_data($data);
                    foreach ($it['images'] as $file) {
                        if (!image_in_use($file, $data['items'])) @unlink(IMAGES_DIR . '/' . basename($file));
                    }
                    $flash = "“{$it['title']}” removed.";
                    break;
                }
                break;

            case 'addcoll':
                $label = trim($_POST['label'] ?? '');
                $slug = slugify($label);
                if ($label === '' || $slug === '') throw new RuntimeException('Give the new category a name.');
                if (in_array($slug, RESERVED, true) || find_collection($data, $slug)) {
                    throw new RuntimeException("“{$label}” already exists or is a reserved name.");
                }
                $data['collections'][] = [
                    'slug' => $slug, 'label' => $label, 'grid' => 'tall',
                    'meta' => trim($_POST['meta'] ?? '') ?: 'Handcrafted in Kashmir',
                    'subs' => [],
                ];
                save_data($data);
                $flash = "Category “{$label}” created — its page is live at collection.html?c={$slug} and it appears in the site menu automatically.";
                break;

            case 'addsub':
                $cslug = $_POST['collection'] ?? '';
                $label = trim($_POST['label'] ?? '');
                $slug = slugify($label);
                if ($label === '' || $slug === '') throw new RuntimeException('Give the subcategory a name.');
                foreach ($data['collections'] as $k => $c) {
                    if ($c['slug'] !== $cslug) continue;
                    foreach ($c['subs'] as $s) {
                        if ($s['slug'] === $slug) throw new RuntimeException("“{$label}” already exists in {$c['label']}.");
                    }
                    $data['collections'][$k]['subs'][] = [
                        'slug' => $slug, 'label' => $label,
                        'meta' => trim($_POST['meta'] ?? ''),
                    ];
                    save_data($data);
                    $flash = "Subcategory “{$label}” added to {$c['label']} — it shows as a filter on that page.";
                    break;
                }
                break;

            case 'delcoll':
                $slug = $_POST['slug'] ?? '';
                if (in_array($slug, BUILTIN, true)) throw new RuntimeException('The four original collections cannot be deleted.');
                foreach ($data['items'] as $it) {
                    if ($it['collection'] === $slug) throw new RuntimeException('Move or delete its products first.');
                }
                foreach ($data['collections'] as $k => $c) {
                    if ($c['slug'] === $slug) {
                        unset($data['collections'][$k]);
                        save_data($data);
                        $flash = "Category “{$c['label']}” deleted.";
                    }
                }
                break;

            case 'delsub':
                $cslug = $_POST['collection'] ?? '';
                $sslug = $_POST['slug'] ?? '';
                foreach ($data['items'] as $it) {
                    if ($it['collection'] === $cslug && ($it['cat'] ?? '') === $sslug) {
                        throw new RuntimeException('Move or delete the products in this subcategory first.');
                    }
                }
                foreach ($data['collections'] as $k => $c) {
                    if ($c['slug'] !== $cslug) continue;
                    foreach ($c['subs'] as $j => $s) {
                        if ($s['slug'] === $sslug) {
                            array_splice($data['collections'][$k]['subs'], $j, 1);
                            save_data($data);
                            $flash = "Subcategory “{$s['label']}” removed from {$c['label']}.";
                            break;
                        }
                    }
                }
                break;
        }
    } catch (RuntimeException $ex) {
        $error = $ex->getMessage();
    }
    $data = load_data();
}

$options = category_options($data);
$items = $data['items'];
$editing = null;
if ($authed && isset($_GET['edit'])) {
    foreach ($items as $it) if ($it['id'] === $_GET['edit']) { $editing = $it; break; }
}
$filter = $_GET['cat'] ?? 'all';
$counts = ['all' => count($items)];
foreach ($items as $it) {
    $k = item_category($data, $it);
    $counts[$k] = ($counts[$k] ?? 0) + 1;
}
$shown = $filter === 'all' ? $items
    : array_values(array_filter($items, fn($it) => item_category($data, $it) === $filter));
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Catalogue manager | House of Naqash</title>
<link rel="icon" href="images/favicon-32.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root { --cream:#faf6ee; --ivory:#f2ebdc; --ink:#1c1712; --gold:#b08a3c; --muted:#837866; --line:rgba(28,23,18,.14); }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font:300 1rem/1.65 "Jost",sans-serif; background:var(--cream); color:#3a332b; padding-bottom:5rem; }
  .bar { background:var(--ink); color:var(--cream); padding:.9rem 0; }
  .bar .wrap { display:flex; justify-content:space-between; align-items:center; }
  .bar a { color:#d6b567; text-decoration:none; font-size:.85rem; letter-spacing:.12em; text-transform:uppercase; }
  .wrap { width:min(1060px,94vw); margin-inline:auto; }
  h1 { font:500 1.15rem "Cormorant Garamond",serif; letter-spacing:.22em; text-transform:uppercase; }
  h2 { font:500 1.9rem "Cormorant Garamond",serif; color:var(--ink); margin:2.4rem 0 1rem; }
  h3 { font:500 1.3rem "Cormorant Garamond",serif; color:var(--ink); }
  .panel { background:#fff; border:1px solid var(--line); padding:1.6rem; margin-top:1.2rem; }
  label { display:block; font:500 .66rem "Jost"; letter-spacing:.24em; text-transform:uppercase; color:var(--muted); margin:1rem 0 .35rem; }
  input[type=text], input[type=password], select, textarea {
    width:100%; font:300 1rem "Jost"; padding:.7rem .85rem; border:1px solid var(--line);
    background:var(--cream); border-radius:0; }
  input:focus, select:focus, textarea:focus { outline:none; border-color:var(--gold); }
  textarea { resize:vertical; }
  .btn { display:inline-block; border:1px solid var(--ink); background:var(--ink); color:var(--cream);
    font:500 .7rem "Jost"; letter-spacing:.24em; text-transform:uppercase; padding:.85rem 1.7rem;
    cursor:pointer; margin-top:1.2rem; }
  .btn:hover { background:var(--gold); border-color:var(--gold); }
  .btn.ghost { background:none; color:var(--ink); }
  .btn.danger { background:none; color:#8c2f2f; border-color:#c9a0a0; padding:.45rem .9rem; margin:0; font-size:.62rem; }
  .btn.tiny { padding:.4rem .8rem; margin:0; font-size:.6rem; }
  .flash { background:#eef5e9; border:1px solid #b9d4ad; padding:.8rem 1rem; margin-top:1.2rem; }
  .err { background:#f8ecec; border:1px solid #d4adad; padding:.8rem 1rem; margin-top:1.2rem; }
  table { width:100%; border-collapse:collapse; margin-top:.6rem; background:#fff; }
  th { font:500 .62rem "Jost"; letter-spacing:.22em; text-transform:uppercase; color:var(--muted); text-align:left; padding:.6rem .8rem; border-bottom:1px solid var(--line); }
  td { padding:.55rem .8rem; border-bottom:1px solid var(--line); vertical-align:middle; font-size:.95rem; }
  td img { width:52px; height:52px; object-fit:cover; display:block; border:1px solid var(--line); }
  .t-title { font:500 1.05rem "Cormorant Garamond",serif; color:var(--ink); }
  .t-meta { font-size:.78rem; color:var(--muted); }
  .row-actions { display:flex; gap:.5rem; justify-content:flex-end; }
  .row-actions a { font:500 .62rem "Jost"; letter-spacing:.2em; text-transform:uppercase; color:var(--gold); text-decoration:none; border:1px solid var(--line); padding:.45rem .9rem; }
  .login { max-width:380px; margin:14vh auto 0; }
  .login h2 { text-align:center; }
  .imgs { display:flex; flex-wrap:wrap; gap:.8rem; margin-top:.4rem; }
  .imgs figure { width:96px; text-align:center; font-size:.7rem; color:var(--muted); }
  .imgs img { width:96px; height:96px; object-fit:cover; border:1px solid var(--line); }
  .hint { font-size:.8rem; color:var(--muted); margin-top:.3rem; }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:0 1.5rem; }
  .grid3 { display:grid; grid-template-columns:2fr 2fr 1fr; gap:0 1rem; align-items:end; }
  .tabs { display:flex; flex-wrap:wrap; gap:.5rem; margin-top:1rem; }
  .tabs a { font:500 .64rem "Jost"; letter-spacing:.18em; text-transform:uppercase; text-decoration:none;
    color:var(--muted); border:1px solid var(--line); padding:.5rem 1rem; background:#fff; }
  .tabs a.on { background:var(--ink); color:var(--cream); border-color:var(--ink); }
  .tabs .n { color:var(--gold); margin-left:.35rem; }
  .cat-list { display:grid; grid-template-columns:1fr 1fr; gap:1.2rem; margin-top:.6rem; }
  .cat-card { background:#fff; border:1px solid var(--line); padding:1.1rem 1.2rem; }
  .cat-card header { display:flex; justify-content:space-between; align-items:center; gap:.6rem; }
  .sub-row { display:flex; justify-content:space-between; align-items:center; padding:.45rem 0; border-top:1px dashed var(--line); font-size:.92rem; }
  .sub-row:first-of-type { margin-top:.7rem; }
  .pill { font:500 .58rem "Jost"; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); }
  details > summary { cursor:pointer; font:500 .68rem "Jost"; letter-spacing:.22em; text-transform:uppercase; color:var(--gold); margin-top:1rem; }
  @media (max-width:760px){ .grid2,.grid3,.cat-list{grid-template-columns:1fr} td:nth-child(3){display:none} }
</style>
</head>
<body>

<div class="bar"><div class="wrap">
  <h1>House of Naqash — Catalogue</h1>
  <?php if ($authed): ?><a href="admin.php?do=logout">Log out</a><?php else: ?><a href="index.html">&larr; Site</a><?php endif; ?>
</div></div>

<div class="wrap">

<?php if (!$authed): ?>
  <div class="login panel">
    <h2>Sign in</h2>
    <?php if ($login_error): ?><div class="err"><?= e($login_error) ?></div><?php endif; ?>
    <form method="post">
      <input type="hidden" name="action" value="login">
      <label for="pw">Password</label>
      <input id="pw" type="password" name="password" autofocus autocomplete="current-password">
      <button class="btn" type="submit">Sign in</button>
    </form>
  </div>

<?php else: ?>

  <?php if ($flash): ?><div class="flash"><?= e($flash) ?></div><?php endif; ?>
  <?php if ($error): ?><div class="err"><?= e($error) ?></div><?php endif; ?>

  <?php if ($editing): $curcat = item_category($data, $editing); ?>
  <h2>Edit “<?= e($editing['title']) ?>”</h2>
  <form class="panel" method="post" enctype="multipart/form-data">
    <input type="hidden" name="action" value="edit">
    <input type="hidden" name="id" value="<?= e($editing['id']) ?>">
    <input type="hidden" name="csrf" value="<?= e($_SESSION['csrf']) ?>">
    <div class="grid2">
      <div>
        <label>Title</label>
        <input type="text" name="title" value="<?= e($editing['title']) ?>" required>
      </div>
      <div>
        <label>Category</label>
        <select name="category">
          <?php foreach ($options as $val => $lab): ?>
          <option value="<?= e($val) ?>" <?= $val === $curcat ? 'selected' : '' ?>><?= e($lab) ?></option>
          <?php endforeach; ?>
        </select>
      </div>
    </div>
    <label>Material / finish (shown under the title)</label>
    <input type="text" name="meta" value="<?= e($editing['meta']) ?>">
    <label>Description</label>
    <textarea name="desc" rows="4"><?= e($editing['desc']) ?></textarea>
    <label>Current photos — tick to remove</label>
    <div class="imgs">
      <?php foreach ($editing['images'] as $img): ?>
      <figure>
        <img src="images/<?= e($img) ?>" alt="">
        <label style="margin:.3rem 0 0; letter-spacing:.06em; text-transform:none;">
          <input type="checkbox" name="remove_images[]" value="<?= e($img) ?>"> remove
        </label>
      </figure>
      <?php endforeach; ?>
    </div>
    <label>Add photos (JPEG, PNG or WebP — you can pick several)</label>
    <input type="file" name="photos[]" accept="image/jpeg,image/png,image/webp" multiple>
    <button class="btn" type="submit">Save changes</button>
    <a class="btn ghost" href="admin.php" style="text-decoration:none; margin-left:.6rem;">Cancel</a>
  </form>
  <?php else: ?>

  <h2>Add a product</h2>
  <form class="panel" method="post" enctype="multipart/form-data">
    <input type="hidden" name="action" value="add">
    <input type="hidden" name="csrf" value="<?= e($_SESSION['csrf']) ?>">
    <div class="grid2">
      <div>
        <label>Title</label>
        <input type="text" name="title" placeholder="e.g. Saffron Garden" required>
      </div>
      <div>
        <label>Category</label>
        <select name="category">
          <?php foreach ($options as $val => $lab): ?>
          <option value="<?= e($val) ?>"><?= e($lab) ?></option>
          <?php endforeach; ?>
        </select>
      </div>
    </div>
    <label>Material / finish (optional — shown under the title)</label>
    <input type="text" name="meta" placeholder="leave blank to use the category default">
    <label>Description</label>
    <textarea name="desc" rows="4" placeholder="A handmade…"></textarea>
    <label>Photos (JPEG, PNG or WebP — you can pick several)</label>
    <input type="file" name="photos[]" accept="image/jpeg,image/png,image/webp" multiple required>
    <p class="hint">The first photo becomes the main one shown on the collection page.</p>
    <button class="btn" type="submit">Add product</button>
  </form>

  <h2>Categories</h2>
  <div class="cat-list">
    <?php foreach ($data['collections'] as $c): ?>
    <div class="cat-card">
      <header>
        <h3><?= e($c['label']) ?></h3>
        <?php if (in_array($c['slug'], BUILTIN, true)): ?>
          <span class="pill">built-in page</span>
        <?php else: ?>
          <form method="post" onsubmit="return confirm('Delete the “<?= e($c['label']) ?>” category?');">
            <input type="hidden" name="action" value="delcoll">
            <input type="hidden" name="slug" value="<?= e($c['slug']) ?>">
            <input type="hidden" name="csrf" value="<?= e($_SESSION['csrf']) ?>">
            <button class="btn danger tiny" type="submit">Delete</button>
          </form>
        <?php endif; ?>
      </header>
      <?php foreach ($c['subs'] as $s): ?>
      <div class="sub-row">
        <span><?= e($s['label']) ?> <span class="pill">filter</span></span>
        <form method="post" onsubmit="return confirm('Remove the “<?= e($s['label']) ?>” subcategory?');">
          <input type="hidden" name="action" value="delsub">
          <input type="hidden" name="collection" value="<?= e($c['slug']) ?>">
          <input type="hidden" name="slug" value="<?= e($s['slug']) ?>">
          <input type="hidden" name="csrf" value="<?= e($_SESSION['csrf']) ?>">
          <button class="btn danger tiny" type="submit">Remove</button>
        </form>
      </div>
      <?php endforeach; ?>
      <details>
        <summary>+ Add subcategory</summary>
        <form method="post">
          <input type="hidden" name="action" value="addsub">
          <input type="hidden" name="collection" value="<?= e($c['slug']) ?>">
          <input type="hidden" name="csrf" value="<?= e($_SESSION['csrf']) ?>">
          <div class="grid3">
            <div><label>Name</label><input type="text" name="label" placeholder="e.g. Silk" required></div>
            <div><label>Default material</label><input type="text" name="meta" placeholder="optional"></div>
            <div><button class="btn tiny" type="submit" style="margin-bottom:.15rem">Add</button></div>
          </div>
        </form>
      </details>
    </div>
    <?php endforeach; ?>

    <div class="cat-card" style="background:var(--ivory)">
      <h3>New category</h3>
      <p class="hint">Creates a new page on the site (it appears in the menu and on the
      homepage automatically once it has products).</p>
      <form method="post">
        <input type="hidden" name="action" value="addcoll">
        <input type="hidden" name="csrf" value="<?= e($_SESSION['csrf']) ?>">
        <div class="grid3">
          <div><label>Name</label><input type="text" name="label" placeholder="e.g. Shawls" required></div>
          <div><label>Default material</label><input type="text" name="meta" placeholder="optional"></div>
          <div><button class="btn tiny" type="submit" style="margin-bottom:.15rem">Create</button></div>
        </div>
      </form>
    </div>
  </div>

  <h2>Products (<?= count($shown) ?><?= $filter !== 'all' ? ' of ' . count($items) : '' ?>)</h2>
  <div class="tabs">
    <a href="admin.php" class="<?= $filter === 'all' ? 'on' : '' ?>">All<span class="n"><?= $counts['all'] ?></span></a>
    <?php foreach ($options as $val => $lab): if (empty($counts[$val])) continue; ?>
    <a href="admin.php?cat=<?= urlencode($val) ?>" class="<?= $filter === $val ? 'on' : '' ?>">
      <?= e($lab) ?><span class="n"><?= $counts[$val] ?></span></a>
    <?php endforeach; ?>
  </div>
  <?php usort($shown, fn($a, $b) => [$a['collection'], $a['title']] <=> [$b['collection'], $b['title']]); ?>
  <table>
    <tr><th></th><th>Title</th><th>Material</th><th>Category</th><th style="text-align:right">Actions</th></tr>
    <?php foreach ($shown as $it): ?>
    <tr>
      <td><img src="images/<?= e($it['images'][0]) ?>" alt="" loading="lazy"></td>
      <td><span class="t-title"><?= e($it['title']) ?></span>
          <?php if (count($it['images']) > 1): ?><span class="t-meta"> · <?= count($it['images']) ?> photos</span><?php endif; ?></td>
      <td class="t-meta"><?= e($it['meta']) ?></td>
      <td class="t-meta"><?= e(category_label($data, $it)) ?></td>
      <td>
        <div class="row-actions">
          <a href="admin.php?edit=<?= urlencode($it['id']) ?>">Edit</a>
          <form method="post" onsubmit="return confirm('Remove “<?= e($it['title']) ?>” from the site?');">
            <input type="hidden" name="action" value="delete">
            <input type="hidden" name="id" value="<?= e($it['id']) ?>">
            <input type="hidden" name="csrf" value="<?= e($_SESSION['csrf']) ?>">
            <button class="btn danger" type="submit">Delete</button>
          </form>
        </div>
      </td>
    </tr>
    <?php endforeach; ?>
  </table>

  <?php endif; ?>
<?php endif; ?>
</div>
</body>
</html>
