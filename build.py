#!/usr/bin/env python3
"""Static site generator for House of Naqash.

The product catalog lives in data/products.json — collection pages fetch it
at runtime and render the grids client-side, so products added through
admin.php (on the server) appear without a rebuild. This script only
generates the page shells.

Edit copy below, then run:  python3 build.py
Generates: index.html, cushions.html, fabrics.html, rugs.html,
           throws.html, contact.html
"""

import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = json.load(open(os.path.join(HERE, "data/products.json")))["items"]

# content hash of the assets — versioned URLs make caches (Varnish, browsers)
# pick up new css/js immediately after a deploy
with open(os.path.join(HERE, "css/style.css"), "rb") as _f:
    _css = _f.read()
with open(os.path.join(HERE, "js/main.js"), "rb") as _f:
    _js = _f.read()
VERSION = hashlib.sha1(_css + _js).hexdigest()[:8]


def coll_items(coll):
    return sorted((i for i in CATALOG if i["collection"] == coll),
                  key=lambda i: i["title"])

WA = "https://wa.me/919419014030"
WA_MSG = WA + "?text=Hello%20House%20of%20Naqash%20%E2%80%94%20I%27d%20like%20to%20enquire%20about%20your%20collections."
IG = "https://www.instagram.com/houseofnaqash/"
TEL = "tel:+919419014030"
PHONE = "+91 94190 14030"

# ------------------------------------------------------------------ chrome --

MARK_SVG = '''<svg class="mark" viewBox="0 0 52 26" fill="none" aria-hidden="true">
  <path d="M2 24 L21 6 L34 18 M9.5 17 V10 H14 V12.8 M26 13.4 L33 7 L50 22 M30 10.2 L36.5 4.5 L52 18.5"
        stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

BOTEH = '''<span class="boteh" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 2c4 3.4 6.4 6.8 6.4 10.5A6.4 6.4 0 1 1 5.6 12.5C5.6 8.8 8 5.4 12 2Z" stroke="currentColor" stroke-width="1.2"/><circle cx="12" cy="13" r="2.4" stroke="currentColor" stroke-width="1.1"/></svg></span>'''

NAV = [("index.html", "Home"), ("cushions.html", "Cushions"),
       ("fabrics.html", "Fabrics"), ("rugs.html", "Rugs"),
       ("curtains.html", "Curtains"), ("throws.html", "Throws")]


def head(title, desc, page, og_image="images/tree-of-life-handmade-chain-stitch-crewel-rug.jpg"):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{og_image}">
<link rel="icon" href="images/favicon-32.png">
<link rel="apple-touch-icon" href="images/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css?v={VERSION}">
</head>
<body data-page="{page}">'''


def header(active):
    active_attr = ' class="active"'
    links = "\n".join(
        f'        <a href="{href}"{active_attr if href == active else ""}>{label}</a>'
        for href, label in NAV)
    return f'''
<a class="skip" href="#main">Skip to content</a>
<header class="site-header" id="siteHeader">
  <div class="wrap header-inner">
    <a class="brand" href="index.html" aria-label="House of Naqash — home">
      <span class="brand-text"><span class="brand-name">House of Naqash<sup class="tm">&trade;</sup></span><span class="brand-sub">Kashmir</span></span>
    </a>
    <nav class="site-nav" id="siteNav" aria-label="Primary">
{links}
      <a href="contact.html" class="nav-enquire{' active' if active == 'contact.html' else ''}">Enquire</a>
    </nav>
    <div class="header-cta">
      <a class="btn btn-line btn-sm" href="contact.html">Enquire</a>
      <button class="nav-toggle" id="navToggle" aria-label="Open menu" aria-expanded="false"><span></span><span></span></button>
    </div>
  </div>
</header>'''


FOOTER = f'''
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <p class="footer-word">House of Naqash<sup class="tm">&trade;</sup></p>
      <p class="footer-blurb">Handcrafted luxury from the Vale of Kashmir, perfected over
      centuries. <em>Naqash</em> — the one who draws; the master designer of Kashmiri craft.</p>
      {BOTEH}
    </div>
    <nav class="footer-col" aria-label="Collections">
      <h4>Collections</h4>
      <a href="cushions.html">Cushions</a>
      <a href="fabrics.html">Fabrics</a>
      <a href="rugs.html">Rugs</a>
      <a href="curtains.html">Curtains</a>
      <a href="throws.html">Throws</a>
    </nav>
    <div class="footer-col">
      <h4>Connect</h4>
      <a href="{TEL}">{PHONE}</a>
      <a href="{WA_MSG}" target="_blank" rel="noopener">WhatsApp</a>
      <a href="{IG}" target="_blank" rel="noopener">Instagram</a>
      <a href="contact.html">Contact us</a>
    </div>
    <div class="footer-col">
      <h4>Atelier</h4>
      <p>Srinagar, Kashmir<br>Visits by appointment</p>
      <p class="footer-tag">A gift for the world,<br><em>from Kashmir.</em></p>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <p>&copy; 2026 House of Naqash. All rights reserved.</p>
    <p>Three generations of craftsmanship · 70+ years</p>
  </div>
</footer>

<div class="detail" id="detail" aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="dTitle">
  <div class="detail-scrim" id="dScrim"></div>
  <div class="detail-panel">
    <button class="d-close" id="dClose" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 7l10 10M17 7L7 17" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button>
    <div class="d-media">
      <button class="d-arrow d-arrow-prev" id="dPrevO" type="button" aria-label="Previous item"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M14.5 5.5 8 12l6.5 6.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <button class="d-zoom" id="dZoom" type="button" title="View full screen">
        <img id="dImg" src="" alt="">
        <span class="d-zoom-hint" aria-hidden="true">&#8599; View full screen</span>
      </button>
      <button class="d-arrow d-arrow-next" id="dNextO" type="button" aria-label="Next item"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9.5 5.5 16 12l-6.5 6.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <div class="d-thumbs" id="dThumbs"></div>
    </div>
    <div class="d-info">
      <p class="d-meta" id="dMeta"></p>
      <h2 class="d-title" id="dTitle"></h2>
      <div class="d-rule">{BOTEH}</div>
      <p class="d-desc" id="dDesc"></p>
      <p class="d-note">Handmade in Srinagar &middot; made to order in custom sizes and palettes.</p>
      <a class="btn btn-solid" id="dEnquire" href="contact.html">Enquire about this piece</a>
      <div class="d-nav">
        <button id="dPrev" type="button">&larr; Previous</button>
        <button id="dNext" type="button">Next &rarr;</button>
      </div>
    </div>
  </div>
</div>

<div class="lightbox" id="lightbox" aria-hidden="true">
  <button class="lb-close" id="lbClose" aria-label="Close">&times;</button>
  <figure>
    <img id="lbImg" src="" alt="">
    <figcaption><span id="lbTitle"></span><span id="lbMeta"></span></figcaption>
  </figure>
</div>

<a class="float-wa" href="{WA_MSG}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.6 0-3.1-.4-4.4-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.6-6.1c-.3-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1-.2.3-.6.8-.8 1-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4 0-.5.2-.7l.4-.5c.1-.2.2-.3.3-.5v-.5c0-.1-.6-1.4-.8-1.9-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.3-.2.3-.9.9-.9 2.2s1 2.5 1.1 2.7c.1.2 1.9 3 4.7 4.2.7.3 1.2.5 1.6.6.7.2 1.3.2 1.8.1.6-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.5-.3Z"/></svg>
</a>

<script src="js/main.js?v={VERSION}"></script>
</body>
</html>'''


def section_head(eyebrow, title, lede=""):
    lede_html = f'\n      <p class="lede reveal">{lede}</p>' if lede else ""
    return f'''      <p class="eyebrow reveal">{eyebrow}</p>
      <h2 class="title reveal">{title}</h2>{lede_html}'''


def collection_hero(eyebrow, title, lede, count_label):
    return f'''
<main id="main">
  <section class="page-hero">
    <div class="wrap">
      <p class="eyebrow reveal">{eyebrow}</p>
      <h1 class="page-title reveal">{title}</h1>
      <p class="lede reveal">{lede}</p>
      <p class="count-label reveal">{BOTEH} <span data-count>{count_label}</span></p>
    </div>
  </section>'''


def product_grid(collection, klass):
    attr = f'data-collection="{collection}"' if collection else 'data-collection-dynamic=""'
    return f'''      <div class="filters reveal" id="filterBar" role="group" aria-label="Filter" style="display:none"></div>
      <div class="product-grid {klass}" id="productGrid" {attr}>
        <noscript><p class="grid-note">Please enable JavaScript to browse the collection,
        or <a href="contact.html">contact us</a> for the full catalogue.</p></noscript>
      </div>'''


# ------------------------------------------------------------------- pages --

def build_index():
    n = {c: len(coll_items(c)) for c in ("cushions", "fabrics", "rugs", "curtains", "throws")}
    return head(
        "House of Naqash | Handmade Interior Luxury from Kashmir",
        "Hand-embroidered cushions, crewel fabrics, chain stitch rugs and throws from the Vale of Kashmir. Three generations of craftsmanship, over 70 years of excellence.",
        "home") + header("index.html") + f'''
<main id="main">
  <section class="hero">
    <div class="hero-copy">
      <p class="eyebrow reveal in">Srinagar, Kashmir &mdash; Three generations</p>
      <h1 class="reveal in">A gift for the <em>world</em>,<br>from Kashmir.</h1>
      <p class="hero-lede reveal in">Hand-embroidered cushions, crewel fabrics, chain stitch rugs
      and pashmina — every thread drawn, stitched and scrutinised by the
      hands of master artisans.</p>
      <div class="hero-actions reveal in">
        <a class="btn btn-solid" href="#collections">Explore the collections</a>
        <a class="btn btn-line" href="contact.html">Speak with us</a>
      </div>
    </div>
    <div class="hero-art reveal in">
      <figure class="ha-rug">
        <img src="images/cushions-at-home-lifestyle.jpg" alt="Hand-embroidered House of Naqash cushions in a living room" fetchpriority="high">
      </figure>
      <figure class="ha-cushion">
        <video src="images/hand-embroidery-atelier.mp4" poster="images/hand-embroidery-atelier-poster.jpg"
               autoplay muted loop playsinline aria-label="An artisan hand-embroidering in the House of Naqash atelier"></video>
      </figure>
      <p class="hero-caption">In your home, from our <em>hands</em> &mdash; embroidered in Srinagar</p>
    </div>
    <div class="scroll-hint" aria-hidden="true"><span></span></div>
  </section>

  <div class="marquee" aria-hidden="true">
    <div class="marquee-track">
      <span>Crewel embroidery</span>{BOTEH}<span>Chain stitch</span>{BOTEH}<span>Silk threadwork</span>{BOTEH}<span>Pashmina</span>{BOTEH}<span>Hand looms</span>{BOTEH}<span>Naqashi drawing</span>{BOTEH}<span>Crewel embroidery</span>{BOTEH}<span>Chain stitch</span>{BOTEH}<span>Silk threadwork</span>{BOTEH}<span>Pashmina</span>{BOTEH}<span>Hand looms</span>{BOTEH}<span>Naqashi drawing</span>{BOTEH}
    </div>
  </div>

  <section class="section heritage">
    <div class="wrap heritage-grid">
      <div class="heritage-copy">
{section_head("Our Story", "Three generations<br>of <em>craftsmanship</em>.")}
        <p class="reveal">For over seventy years, our family has practised the patient arts of
        the Vale of Kashmir — crewel work, chain stitch, sozni and naqashi — passing needle and
        pattern from father to son, hand to hand.</p>
        <p class="reveal">Every thread, every stitch and every colour is scrutinised before a
        piece leaves our hands. It is slow work. We would not have it any other way.</p>
        <div class="stats reveal">
          <div class="stat"><span class="stat-n">70<sup>+</sup></span><span class="stat-l">Years of excellence</span></div>
          <div class="stat"><span class="stat-n">3</span><span class="stat-l">Generations</span></div>
          <div class="stat"><span class="stat-n">100<sup>%</sup></span><span class="stat-l">Made by hand</span></div>
        </div>
      </div>
      <div class="heritage-media">
        <figure class="hm-main reveal"><img src="images/exhibition-naqash-stand.jpg" alt="House of Naqash exhibition — handmade cushions and crewel fabrics" loading="lazy"></figure>
        <figure class="hm-small reveal" style="transition-delay:150ms"><img src="images/exhibition-showroom-wall.jpg" alt="Naqash textiles on display" loading="lazy"></figure>
      </div>
    </div>
  </section>

  <section class="section" id="collections">
    <div class="wrap">
{section_head("The Collections", "Five crafts, one <em>lineage</em>.", "Every piece begins as a drawing — a naqashi — and passes through months of hand embroidery before it earns our name.")}
      <div class="collection-grid">
        <a class="c-card span-7 reveal" href="cushions.html">
          <img src="images/festival-birds-handmade-modern-cushion-cover.jpg" alt="Hand-embroidered silk cushion covers" loading="lazy">
          <div class="c-overlay"><p class="c-count" data-collection-count="cushions">{n['cushions']} designs</p><h3>Cushions</h3><span class="c-link">Explore <i>&rarr;</i></span></div>
        </a>
        <a class="c-card span-5 reveal" href="fabrics.html" style="transition-delay:120ms">
          <img src="images/paisley-garden-crewel-hand-embroidered-cotton-fabric.jpg" alt="Crewel hand-embroidered cotton fabrics" loading="lazy">
          <div class="c-overlay"><p class="c-count" data-collection-count="fabrics">{n['fabrics']} designs</p><h3>Fabrics</h3><span class="c-link">Explore <i>&rarr;</i></span></div>
        </a>
        <a class="c-card span-5 reveal" href="rugs.html">
          <img src="images/classic-medallion-handmade-chain-stitch-rug.jpg" alt="Handmade chain stitch rugs" loading="lazy">
          <div class="c-overlay"><p class="c-count" data-collection-count="rugs">{n['rugs']} designs</p><h3>Rugs</h3><span class="c-link">Explore <i>&rarr;</i></span></div>
        </a>
        <a class="c-card span-7 reveal" href="throws.html" style="transition-delay:120ms">
          <img src="images/neutral-crewel-fabric-swatch-set.jpg" alt="Crewel throws and textiles" loading="lazy">
          <div class="c-overlay"><p class="c-count">Private portfolio</p><h3>Throws</h3><span class="c-link">Explore <i>&rarr;</i></span></div>
        </a>
        <a class="c-card span-12 reveal" href="curtains.html">
          <img src="images/golden-jacobean-crewel-curtain.jpg" alt="Crewel hand-embroidered curtains" loading="lazy">
          <div class="c-overlay"><p class="c-count" data-collection-count="curtains">{n['curtains']} designs</p><h3>Curtains</h3><span class="c-link">Explore <i>&rarr;</i></span></div>
        </a>
      </div>
    </div>
  </section>

  <section class="section section-dark craft">
    <div class="wrap craft-grid">
      <div class="craft-main">
{section_head("The Craft", "From drawing<br>to <em>heirloom</em>.")}
        <div class="craft-steps">
          <div class="craft-step reveal">
            <span class="step-n">01</span>
            <h3>Naqashi &mdash; the drawing</h3>
            <p>Each design begins with the naqash, the master draughtsman, who draws the pattern
            freehand and perforates it onto cloth — a craft kept within families for centuries.</p>
          </div>
          <div class="craft-step reveal" style="transition-delay:130ms">
            <span class="step-n">02</span>
            <h3>The stitch</h3>
            <p>Artisans work silk and wool thread through cotton and pashmina, one stitch at a
            time. A single rug or shawl can carry months of a craftsman&rsquo;s days.</p>
          </div>
          <div class="craft-step reveal" style="transition-delay:260ms">
            <span class="step-n">03</span>
            <h3>The scrutiny</h3>
            <p>Before anything leaves Srinagar, every thread, every stitch and every colour is
            examined against the original drawing. Only then does it carry our name.</p>
          </div>
        </div>
      </div>
      <figure class="craft-media reveal" style="transition-delay:150ms">
        <video src="images/chain-stitch-under-hand.mp4" poster="images/chain-stitch-under-hand-poster.jpg"
               muted loop playsinline preload="metadata" data-autoplay
               aria-label="Chain stitch embroidery under an artisan's hand"></video>
        <figcaption>Chain stitch, under the hand &mdash; Srinagar atelier</figcaption>
      </figure>
    </div>
    <div class="wrap">
      <blockquote class="craft-quote reveal">
        {BOTEH}
        <p>&ldquo;Every thread, every stitch and every colour is scrutinised —<br>
        <em>that</em> is the House of Naqash.&rdquo;</p>
      </blockquote>
    </div>
  </section>

  <section class="section bespoke">
    <div class="wrap bespoke-grid">
      <div class="bespoke-media reveal">
        <img src="images/embroidered-throw-bedroom.jpg" alt="Hand-embroidered suzani throw styled on a bed — the finished piece" loading="lazy">
        <video src="images/crewel-fabric-touch.mp4" poster="images/crewel-fabric-touch-poster.jpg"
               muted loop playsinline preload="metadata" data-autoplay
               aria-label="The same embroidery being worked by hand in the atelier"></video>
        <p class="bespoke-caption">The piece, and its making &mdash; one commission, from drawing to delivery.</p>
      </div>
      <div class="bespoke-copy">
{section_head("Bespoke", "Intricate, <em>customisable</em> designs.")}
        <p class="reveal">Beyond the collections — silk and woollen cushions, fabrics by the
        metre, throws, chain stitch rugs, bags and pouches, pashmina shawls, wall art and lamp
        shades — we work to commission.</p>
        <p class="reveal">Your palette, your dimensions, your pattern. Share a reference or a
        room, and our naqash will draw it for you.</p>
        <a class="btn btn-line reveal" href="contact.html">Begin a commission</a>
      </div>
    </div>
  </section>

  <section class="cta-band">
    <div class="wrap">
      <p class="eyebrow reveal">More ways to connect</p>
      <h2 class="cta-title reveal">Reimagine your <em>space</em> with us.</h2>
      <div class="hero-actions center reveal">
        <a class="btn btn-gold" href="contact.html">Enquire</a>
        <a class="btn btn-line-light" href="{TEL}">Call {PHONE}</a>
      </div>
    </div>
  </section>
</main>''' + FOOTER


def build_cushions():
    items = coll_items("cushions")
    return head(
        "Cushions | House of Naqash",
        f"{len(items)} hand-embroidered silk and woollen cushion covers from Kashmir — art, modern and classic crewel designs.",
        "cushions") + header("cushions.html") + collection_hero(
        "The Collections", "Cushions",
        "Silk-thread art pieces and woollen crewel classics — each cover embroidered by hand over weeks, finished and scrutinised in Srinagar.",
        f"{len(items)} designs") + f'''
  <section class="section grid-section">
    <div class="wrap">
{product_grid("cushions", "square")}
    </div>
  </section>
</main>''' + FOOTER


def build_fabrics():
    items = coll_items("fabrics")
    return head(
        "Fabrics | House of Naqash",
        f"{len(items)} crewel hand-embroidered cotton fabrics from Kashmir — upholstery, drapery and handloom designs by the metre.",
        "fabrics") + header("fabrics.html") + collection_hero(
        "The Collections", "Fabrics",
        "Crewel hand-embroidered cotton by the metre — wool and silk thread worked over handloom cloth, for upholstery, drapery and walls.",
        f"{len(items)} designs") + f'''
  <section class="section grid-section">
    <div class="wrap">
{product_grid("fabrics", "tall")}
    </div>
  </section>
</main>''' + FOOTER


def build_rugs():
    items = coll_items("rugs")
    return head(
        "Rugs | House of Naqash",
        f"{len(items)} handmade chain stitch rugs from Kashmir — wool and crewel designs, medallions, gardens and modern art pieces.",
        "rugs") + header("rugs.html") + collection_hero(
        "The Collections", "Rugs",
        "Handmade chain stitch rugs — hook-worked wool on cotton in unbroken chains, from classic Kashmiri medallions to modern art pieces.",
        f"{len(items)} designs") + f'''
  <section class="section grid-section">
    <div class="wrap">
{product_grid("rugs", "rug")}
    </div>
  </section>
</main>''' + FOOTER


def build_throws():
    it = coll_items("throws")[0]
    return head(
        "Throws | House of Naqash",
        "Hand-embroidered crewel throws from Kashmir — a privately curated portfolio, shared on enquiry.",
        "throws") + header("throws.html") + collection_hero(
        "The Collections", "Throws",
        "Crewel and silk-thread throws, embroidered edge to edge.",
        "A private portfolio") + f'''
  <section class="section">
    <div class="wrap throws-grid">
      <figure class="throws-media reveal">
        <img src="images/{it['images'][0]}" alt="{it['title']} — House of Naqash throws" loading="lazy">
      </figure>
      <div class="throws-copy">
{section_head("By Appointment", "A collection shared <em>privately</em>.")}
        <p class="reveal">{it['desc']}</p>
        <p class="reveal">Our throws are made in small numbers and move quickly — so we share the
        current portfolio personally rather than publishing it. Tell us your palette and room,
        and we will send what is on the loom and in the atelier today.</p>
        <div class="hero-actions reveal">
          <a class="btn btn-solid" href="{WA_MSG}" target="_blank" rel="noopener">Request the portfolio</a>
          <a class="btn btn-line" href="{TEL}">{PHONE}</a>
        </div>
        <p class="reveal also-like">You may also like our <a href="fabrics.html">fabrics</a> and <a href="cushions.html">cushions</a>.</p>
      </div>
    </div>
  </section>

  <section class="section grid-section throws-portfolio">
    <div class="wrap">
{section_head("Recent Work", "A <em>glimpse</em> of the portfolio.")}
{product_grid("throws", "tall")}
    </div>
  </section>
</main>''' + FOOTER


def build_curtains():
    items = coll_items("curtains")
    return head(
        "Curtains | House of Naqash",
        f"{len(items)} crewel hand-embroidered curtains from Kashmir — wool-thread florals and vines worked over cotton, made to filter light and dress a room.",
        "curtains") + header("curtains.html") + collection_hero(
        "The Collections", "Curtains",
        "Crewel hand-embroidered curtains — wool thread worked freehand over cotton, from airy ivory grounds to richly coloured Jacobean florals.",
        f"{len(items)} designs") + f'''
  <section class="section grid-section">
    <div class="wrap">
{product_grid("curtains", "tall")}
    </div>
  </section>
</main>''' + FOOTER


def build_contact():
    return head(
        "Contact | House of Naqash",
        "Speak with House of Naqash — call or WhatsApp +91 94190 14030, or find us on Instagram. Atelier in Srinagar, Kashmir; visits by appointment.",
        "contact") + header("contact.html") + collection_hero(
        "More ways to connect", "Reimagine your <em>space</em> with us.",
        "A conversation is the best place to begin — about a collection piece, a commission, or simply Kashmir.",
        "We usually reply within a day") + f'''
  <section class="section contact-section">
    <div class="wrap contact-grid">
      <div class="contact-cards">
        <a class="contact-card reveal" href="{TEL}">
          <span class="cc-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2Z"/></svg></span>
          <span class="cc-label">Call us</span>
          <span class="cc-value">{PHONE}</span>
        </a>
        <a class="contact-card reveal" style="transition-delay:110ms" href="{WA_MSG}" target="_blank" rel="noopener">
          <span class="cc-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3Z"/><path d="M9 9.5c.5 2.5 2.5 4.5 5 5l1.5-1.5 2 1c-.5 1.5-1.5 2-3 2-3.5 0-7-3.5-7-7 0-1.5.5-2.5 2-3l1 2L9 9.5Z" stroke-width="1.1"/></svg></span>
          <span class="cc-label">WhatsApp</span>
          <span class="cc-value">Message us anytime</span>
        </a>
        <a class="contact-card reveal" style="transition-delay:220ms" href="{IG}" target="_blank" rel="noopener">
          <span class="cc-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="3.5" y="3.5" width="17" height="17" rx="4.5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/></svg></span>
          <span class="cc-label">Instagram</span>
          <span class="cc-value">@houseofnaqash</span>
        </a>
        <div class="contact-card static reveal" style="transition-delay:330ms">
          <span class="cc-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11Z"/><circle cx="12" cy="10" r="2.6"/></svg></span>
          <span class="cc-label">Atelier</span>
          <span class="cc-value">Srinagar, Kashmir &mdash; by appointment</span>
        </div>
      </div>
      <div class="contact-form-wrap reveal" style="transition-delay:150ms">
        <h3 class="form-title">Send an enquiry</h3>
        <p class="form-sub">We&rsquo;ll reply by email or phone, usually within a day.</p>
        <form id="enquiryForm" novalidate>
          <label>Your name<input type="text" id="fName" name="from_name" autocomplete="name" required></label>
          <div class="form-row">
            <label>Email<input type="email" id="fEmail" name="reply_to" autocomplete="email" placeholder="you@example.com"></label>
            <label>Phone<input type="tel" id="fPhone" name="phone" autocomplete="tel" placeholder="+91&hellip;"></label>
          </div>
          <p class="form-hint">{BOTEH} Add at least one &mdash; email or phone &mdash; so we can reach you.</p>
          <label>I&rsquo;m interested in
            <select id="fTopic" name="topic" data-topics>
              <option>A bespoke commission</option><option>Something else</option>
            </select>
          </label>
          <label>Message<textarea id="fMsg" name="message" rows="5" placeholder="Tell us about your space, palette, or the piece you have in mind&hellip;"></textarea></label>
          <input type="text" id="fCompany" name="company" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="form-actions">
            <button class="btn btn-solid" type="submit" id="sendEmail">Send enquiry</button>
            <button class="btn btn-line" type="button" id="sendWa">Send via WhatsApp</button>
          </div>
          <p class="form-status" id="formStatus" role="status" aria-live="polite"></p>
        </form>
      </div>
    </div>
  </section>
</main>
<script src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
<script>window.HON_EMAILJS={{publicKey:"fL3GUK2hq0_qEehx_",service:"service_26s186g",template:"template_4qcryhf"}};</script>''' + FOOTER


def build_collection():
    """Generic page for collections created in the admin (collection.html?c=slug)."""
    return head(
        "Collections | House of Naqash",
        "Handcrafted Kashmiri interiors from House of Naqash — hand embroidered in Srinagar.",
        "collection") + header("") + collection_hero(
        "The Collections", "Collection",
        "Handcrafted in Srinagar — every piece drawn, stitched and scrutinised by hand before it carries our name.",
        "&nbsp;") + f'''
  <section class="section grid-section">
    <div class="wrap">
{product_grid("", "tall")}
    </div>
  </section>
</main>''' + FOOTER


PAGES = {
    "index.html": build_index,
    "cushions.html": build_cushions,
    "fabrics.html": build_fabrics,
    "rugs.html": build_rugs,
    "throws.html": build_throws,
    "curtains.html": build_curtains,
    "contact.html": build_contact,
    "collection.html": build_collection,
}

if __name__ == "__main__":
    for name, fn in PAGES.items():
        html = fn()
        with open(os.path.join(HERE, name), "w") as f:
            f.write(html)
        print(f"wrote {name} ({len(html):,} bytes)")
