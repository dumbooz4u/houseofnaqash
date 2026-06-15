# House of Naqash — Website

A modern, luxury static website for [houseofnaqash.com](https://www.houseofnaqash.com),
built from the existing site's content and product photography.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Homepage — hero (Tree of Life rug + Festival Birds cushion), heritage story, collections, craft process, bespoke, contact CTA |
| `cushions.html` | 40 cushion designs with Silk / Woollen filters |
| `fabrics.html` | 45 crewel hand-embroidered cotton fabrics |
| `rugs.html` | 53 handmade chain stitch rugs |
| `throws.html` | "By appointment" private portfolio page |
| `contact.html` | Contact cards + enquiry form that opens WhatsApp pre-filled |

Clicking any item opens a detail view with its original description, all
associated photos (with thumbnails where an item has multiple views),
full-screen zoom, an item-specific WhatsApp enquiry button, and
previous / next navigation.

## Managing products

The catalogue is dynamic. On the live server, open **`/admin.php`** and sign
in — you can add a product (title, category, material, description, one or
more photos), edit it, or delete it, and it appears on the right collection
page immediately. No rebuild or redeploy needed.

Categories are managed there too: create a new category (it gets its own
page at `collection.html?c=slug` and appears in the site menu and on the
homepage automatically once it has products), or add subcategories to any
category — they show as filter buttons on that collection's page, the way
Silk/Woollen work on Cushions. The four original collections keep their
dedicated designed pages and can't be deleted; categories and subcategories
can only be deleted once they hold no products. The products table in the
admin can be filtered by category via the tabs above it.

- The live catalogue lives in `data/products.json` **on the server** — that
  copy is the source of truth once you start using admin.php. `deploy.sh`
  deliberately never uploads it.
- To change the admin password:
  `php -r 'echo password_hash("new-password", PASSWORD_DEFAULT);'`
  and paste the hash into `PASSWORD_HASH` in `admin.php`, then redeploy.

## How it's built

- `data/products.json` — the product catalog (seeded from the original
  site's 138 items). Collection pages fetch it and render their grids
  client-side; `items_data.json` is the original scrape, kept as a backup.
- `build.py` — generates the six HTML page shells plus the copy at the top
  of the file. Edit, then run `python3 build.py`.
- `images/` — all 147 images, stored locally (nothing is hotlinked).
  Product photos keep their descriptive names
  (`classic-medallion-handmade-chain-stitch-rug.jpg`); brand and editorial
  shots are named by content (`exhibition-naqash-stand.jpg`,
  `studio-crewel-shawl-emerald.png`, `favicon-32.png`).
- `css/style.css` — the design system (ivory & ink palette, gold accents,
  Cormorant Garamond + Jost, scroll reveals, detail modal, responsive).
- `js/main.js` — header behaviour, mobile nav, scroll reveals, item detail
  modal + zoom, collection filters, WhatsApp enquiry form.

No build tooling, no frameworks — host the HTML/CSS/JS/images anywhere.

## Preview locally

```sh
python3 -m http.server 8743
# open http://localhost:8743
```
