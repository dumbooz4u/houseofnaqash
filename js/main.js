/* House of Naqash — interactions */
(function () {
  "use strict";

  var BUILTIN_PAGES = ["cushions", "fabrics", "rugs", "throws"];
  var DEFAULT_COLLECTIONS = [
    { slug: "cushions", label: "Cushions", grid: "square", subs: [
      { slug: "silk", label: "Silk" }, { slug: "wool", label: "Woollen" }] },
    { slug: "fabrics", label: "Fabrics", grid: "tall", subs: [] },
    { slug: "rugs", label: "Rugs", grid: "rug", subs: [] },
    { slug: "throws", label: "Throws", grid: "tall", subs: [] }
  ];

  function pageFor(slug) {
    return BUILTIN_PAGES.indexOf(slug) >= 0
      ? slug + ".html"
      : "collection.html?c=" + encodeURIComponent(slug);
  }

  /* Header: hairline + tighter padding once scrolled */
  var header = document.getElementById("siteHeader");
  function onScroll() {
    header.classList.toggle("scrolled", window.scrollY > 24);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Mobile navigation */
  var toggle = document.getElementById("navToggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.getElementById("siteNav").addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        document.body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* Reveal on scroll */
  var io = null;
  if ("IntersectionObserver" in window) {
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
  }
  function observeReveal(scope) {
    (scope || document).querySelectorAll(".reveal:not(.in)").forEach(function (el) {
      if (io) io.observe(el);
      else el.classList.add("in");
    });
  }
  observeReveal(document);

  /* ------------------------------------------------- product catalog -- */

  var catalogPromise = null;
  function fetchCatalog() {
    if (!catalogPromise) {
      // unique query string defeats any intermediate cache (e.g. Varnish)
      catalogPromise = fetch("data/products.json?v=" + Date.now(), { cache: "no-store" })
        .then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.json();
        })
        .then(function (d) {
          return {
            items: d.items || [],
            collections: (d.collections && d.collections.length)
              ? d.collections : DEFAULT_COLLECTIONS
          };
        });
    }
    return catalogPromise;
  }

  function itemsFor(cat, slug) {
    return cat.items
      .filter(function (it) { return it.collection === slug; })
      .sort(function (a, b) { return a.title.localeCompare(b.title); });
  }

  /* Navigation + footer: append collections created in the admin */
  fetchCatalog().then(function (cat) {
    var extras = cat.collections.filter(function (c) {
      return BUILTIN_PAGES.indexOf(c.slug) < 0;
    });
    if (!extras.length) return;
    var nav = document.getElementById("siteNav");
    var anchor = nav && nav.querySelector('a[href="contact.html"]');
    var footNav = document.querySelector('.footer-col[aria-label="Collections"]');
    extras.forEach(function (c) {
      if (nav && anchor) {
        var a = document.createElement("a");
        a.href = pageFor(c.slug);
        a.textContent = c.label;
        if (document.body.dataset.page === "collection-" + c.slug) a.className = "active";
        nav.insertBefore(a, anchor);
      }
      if (footNav) {
        var f = document.createElement("a");
        f.href = pageFor(c.slug);
        f.textContent = c.label;
        footNav.appendChild(f);
      }
    });
  }).catch(function () {});

  /* Homepage: live counts + cards for admin-created collections */
  if (document.body.dataset.page === "home") {
    fetchCatalog().then(function (cat) {
      document.querySelectorAll("[data-collection-count]").forEach(function (n) {
        var c = itemsFor(cat, n.dataset.collectionCount).length;
        n.textContent = c + " designs";
      });
      var grid = document.querySelector(".collection-grid");
      if (!grid) return;
      /* only collections that have products and aren't one of the 4 built-ins */
      var extras = cat.collections.filter(function (c) {
        return BUILTIN_PAGES.indexOf(c.slug) < 0 && itemsFor(cat, c.slug).length;
      });
      extras.forEach(function (c, i) {
        var items = itemsFor(cat, c.slug);
        /* keep each row summing to 12 cols; a lone trailing card spans full width */
        var span = (i === extras.length - 1 && extras.length % 2 === 1)
          ? "span-12" : (i % 2 === 0 ? "span-7" : "span-5");
        var a = document.createElement("a");
        a.className = "c-card " + span + " reveal";
        a.href = pageFor(c.slug);
        var img = document.createElement("img");
        img.src = "images/" + items[0].images[0];
        img.alt = c.label + " — House of Naqash";
        img.loading = "lazy";
        var ov = document.createElement("div");
        ov.className = "c-overlay";
        ov.innerHTML = '<p class="c-count"></p><h3></h3>' +
          '<span class="c-link">Explore <i>&rarr;</i></span>';
        ov.querySelector(".c-count").textContent = items.length + " designs";
        ov.querySelector("h3").textContent = c.label;
        a.appendChild(img);
        a.appendChild(ov);
        grid.appendChild(a);
      });
      observeReveal(grid);
    }).catch(function () {});
  }

  /* Brand spinner: hairline ring spinning around a pulsing boteh */
  function makeSpinner() {
    var d = document.createElement("div");
    d.className = "hon-spinner";
    d.setAttribute("role", "status");
    d.setAttribute("aria-label", "Loading");
    d.innerHTML = '<span class="ring"></span>' +
      '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
      '<path d="M12 2c4 3.4 6.4 6.8 6.4 10.5A6.4 6.4 0 1 1 5.6 12.5C5.6 8.8 8 5.4 12 2Z" stroke="currentColor" stroke-width="1.2"/>' +
      '<circle cx="12" cy="13" r="2.4" stroke="currentColor" stroke-width="1.1"/></svg>';
    return d;
  }
  function spinnerRow() {
    var holder = document.createElement("div");
    holder.className = "grid-sentinel";
    holder.appendChild(makeSpinner());
    return holder;
  }

  /* Collection pages: render the grid in batches as the visitor scrolls,
     so photos are only requested when they're about to be seen. */
  var grid = document.querySelector("#productGrid[data-collection], #productGrid[data-collection-dynamic]");
  var gridItems = [];
  var renderedCount = 0;
  var sentinel = null;
  var BATCH = 12;

  var sentinelIO = ("IntersectionObserver" in window)
    ? new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            sentinelIO.unobserve(e.target);
            appendBatch();
          }
        });
      }, { rootMargin: "600px 0px" })
    : null;

  if (grid) {
    grid.textContent = "";
    grid.appendChild(spinnerRow());
    fetchCatalog().then(function (cat) {
      var slug = grid.dataset.collection;
      if (!slug) {
        slug = new URLSearchParams(location.search).get("c") || "";
        grid.dataset.collection = slug;
      }
      var coll = null;
      cat.collections.forEach(function (c) { if (c.slug === slug) coll = c; });

      /* generic collection.html: fill in the hero */
      if (grid.hasAttribute("data-collection-dynamic")) {
        if (!coll) { location.replace("index.html"); return; }
        document.title = coll.label + " | House of Naqash";
        var t = document.querySelector(".page-title");
        if (t) t.textContent = coll.label;
        document.body.dataset.page = "collection-" + slug;
        grid.className = "product-grid " + (coll.grid || "tall");
      }

      gridItems = itemsFor(cat, slug);
      grid.textContent = "";
      appendBatch();
      var count = document.querySelector("[data-count]");
      if (count) count.textContent = gridItems.length + " designs";
      renderFilters(coll, gridItems);
      initDetail(gridItems);
    }).catch(function (err) {
      grid.innerHTML = '<p class="grid-note">The collection could not be loaded. ' +
        'Please refresh, or <a href="contact.html">contact us</a> for the catalogue.</p>';
      if (window.console) console.error(err);
    });
  }

  function buildCard(it, i) {
    var fig = document.createElement("figure");
    fig.className = "p-card reveal";
    fig.dataset.cat = it.cat || "";
    fig.style.transitionDelay = (i % 4) * 70 + "ms";

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "p-media";
    btn.dataset.idx = i;
    btn.setAttribute("aria-label", "View " + it.title + " — details and photos");

    var img = document.createElement("img");
    img.alt = it.title + " — " + it.meta + ", House of Naqash";
    img.loading = "lazy";
    img.decoding = "async";
    img.addEventListener("load", function () { btn.classList.add("img-ok"); });
    img.addEventListener("error", function () { btn.classList.add("img-ok"); });
    img.src = "images/" + it.images[0];
    if (img.complete && img.naturalWidth) btn.classList.add("img-ok");
    btn.appendChild(img);

    if (it.images.length > 1) {
      var more = document.createElement("span");
      more.className = "p-more";
      more.textContent = it.images.length + " views";
      btn.appendChild(more);
    }

    var cap = document.createElement("figcaption");
    var name = document.createElement("h3");
    name.className = "p-name";
    name.textContent = it.title;
    var meta = document.createElement("p");
    meta.className = "p-meta";
    meta.textContent = it.meta;
    cap.appendChild(name);
    cap.appendChild(meta);

    fig.appendChild(btn);
    fig.appendChild(cap);
    return fig;
  }

  function appendBatch() {
    if (sentinel) { sentinel.remove(); sentinel = null; }
    var end = sentinelIO ? Math.min(renderedCount + BATCH, gridItems.length) : gridItems.length;
    for (var i = renderedCount; i < end; i++) {
      grid.appendChild(buildCard(gridItems[i], i));
    }
    renderedCount = end;
    observeReveal(grid);
    if (renderedCount < gridItems.length) {
      sentinel = spinnerRow();
      grid.appendChild(sentinel);
      sentinelIO.observe(sentinel);
    }
  }

  /* render everything that's left (needed before filtering) */
  function renderRest() {
    if (renderedCount >= gridItems.length) return;
    if (sentinel) { sentinel.remove(); sentinel = null; }
    for (var i = renderedCount; i < gridItems.length; i++) {
      grid.appendChild(buildCard(gridItems[i], i));
    }
    renderedCount = gridItems.length;
    observeReveal(grid);
  }

  /* Sub-category filter bar, built from the collection's subs */
  function renderFilters(coll, items) {
    var holder = document.getElementById("filterBar");
    if (!holder) return;
    var subs = (coll && coll.subs) || [];
    /* only show filters for subs that actually have items */
    subs = subs.filter(function (s) {
      return items.some(function (it) { return it.cat === s.slug; });
    });
    if (subs.length < 2) { holder.style.display = "none"; return; }

    holder.style.display = "";
    holder.textContent = "";
    var all = [{ slug: "all", label: "All" }].concat(subs);
    all.forEach(function (s, i) {
      var b = document.createElement("button");
      b.className = "filter" + (i === 0 ? " active" : "");
      b.dataset.filter = s.slug;
      b.textContent = s.label;
      b.addEventListener("click", function () {
        renderRest(); /* every card must exist before we can filter them */
        holder.querySelectorAll(".filter").forEach(function (x) { x.classList.remove("active"); });
        b.classList.add("active");
        grid.querySelectorAll(".p-card").forEach(function (card) {
          card.classList.toggle("hidden", s.slug !== "all" && card.dataset.cat !== s.slug);
        });
      });
      holder.appendChild(b);
    });
  }

  /* ------------------------------------------------ item detail modal -- */

  function initDetail(items) {
    var detail = document.getElementById("detail");
    var lb = document.getElementById("lightbox");
    if (!detail || !items.length) return;

    var dImg = document.getElementById("dImg");
    var dZoom = document.getElementById("dZoom");
    var dMeta = document.getElementById("dMeta");
    var dTitle = document.getElementById("dTitle");
    var dDesc = document.getElementById("dDesc");
    var dThumbs = document.getElementById("dThumbs");
    var dEnquire = document.getElementById("dEnquire");
    var current = -1;
    var currentImg = 0;

    /* loading spinner inside the image stage */
    var dSpin = makeSpinner();
    dSpin.classList.add("d-spin");
    dZoom.appendChild(dSpin);
    function imgDone() { dZoom.classList.remove("loading"); }
    dImg.addEventListener("load", imgDone);
    dImg.addEventListener("error", imgDone);

    function lockScroll(lock) {
      document.body.style.overflow = lock ? "hidden" : "";
    }

    function visibleIndices() {
      var out = [];
      grid.querySelectorAll(".p-media[data-idx]").forEach(function (t) {
        var card = t.closest(".p-card");
        if (!card || !card.classList.contains("hidden")) {
          out.push(parseInt(t.dataset.idx, 10));
        }
      });
      return out;
    }

    function setImage(i) {
      currentImg = i;
      var it = items[current];
      /* hide the stale photo and show the spinner until the new one loads */
      dZoom.classList.add("loading");
      dImg.removeAttribute("src");
      dImg.src = "images/" + it.images[i];
      dImg.alt = it.title + " — view " + (i + 1);
      if (dImg.complete && dImg.naturalWidth) imgDone();
      dThumbs.querySelectorAll("button").forEach(function (b, j) {
        b.classList.toggle("active", j === i);
      });
    }

    function openDetail(idx) {
      current = idx;
      var it = items[idx];
      dMeta.textContent = it.meta;
      dTitle.textContent = it.title;
      dDesc.textContent = it.desc;
      dEnquire.href = "https://wa.me/919419014030?text=" + encodeURIComponent(
        'Hello House of Naqash — I’m interested in the "' + it.title +
        '" (' + it.meta + "). Could you share details?"
      );
      dThumbs.innerHTML = "";
      dThumbs.style.display = it.images.length > 1 ? "" : "none";
      it.images.forEach(function (img, j) {
        var b = document.createElement("button");
        b.type = "button";
        b.setAttribute("aria-label", "View photo " + (j + 1) + " of " + it.images.length);
        var im = document.createElement("img");
        im.src = "images/" + img;
        im.alt = "";
        b.appendChild(im);
        b.addEventListener("click", function () { setImage(j); });
        dThumbs.appendChild(b);
      });
      setImage(0);
      detail.classList.add("open");
      detail.setAttribute("aria-hidden", "false");
      lockScroll(true);
    }

    function closeDetail() {
      detail.classList.remove("open");
      detail.setAttribute("aria-hidden", "true");
      lockScroll(false);
    }

    function step(dir) {
      var vis = visibleIndices();
      if (!vis.length) return;
      var pos = vis.indexOf(current);
      openDetail(vis[(pos + dir + vis.length) % vis.length]);
    }

    /* delegated, so cards rendered in later batches work too */
    grid.addEventListener("click", function (e) {
      var t = e.target.closest(".p-media[data-idx]");
      if (t) openDetail(parseInt(t.dataset.idx, 10));
    });

    document.getElementById("dClose").addEventListener("click", closeDetail);
    document.getElementById("dScrim").addEventListener("click", closeDetail);
    document.getElementById("dPrev").addEventListener("click", function () { step(-1); });
    document.getElementById("dNext").addEventListener("click", function () { step(1); });
    document.getElementById("dPrevO").addEventListener("click", function () { step(-1); });
    document.getElementById("dNextO").addEventListener("click", function () { step(1); });

    /* full-screen zoom of the current photo */
    var lbImg = document.getElementById("lbImg");
    var lbTitle = document.getElementById("lbTitle");
    var lbMeta = document.getElementById("lbMeta");

    function openZoom() {
      var it = items[current];
      lbImg.src = "images/" + it.images[currentImg];
      lbImg.alt = it.title;
      lbTitle.textContent = it.title;
      lbMeta.textContent = it.meta;
      lb.classList.add("open");
      lb.setAttribute("aria-hidden", "false");
    }
    function closeZoom() {
      lb.classList.remove("open");
      lb.setAttribute("aria-hidden", "true");
    }

    document.getElementById("dZoom").addEventListener("click", openZoom);
    document.getElementById("lbClose").addEventListener("click", closeZoom);
    lb.addEventListener("click", function (e) { if (e.target === lb) closeZoom(); });

    document.addEventListener("keydown", function (e) {
      if (lb.classList.contains("open")) {
        if (e.key === "Escape") closeZoom();
        return;
      }
      if (!detail.classList.contains("open")) return;
      if (e.key === "Escape") closeDetail();
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
    });
  }

  /* Videos: hero loop starts immediately; data-autoplay loops play only
     while on screen. Both respect reduced-motion. */
  var reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function tryPlay(v) {
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  }

  var heroVideo = document.querySelector(".ha-cushion video");
  if (heroVideo) {
    if (reduceMotion) {
      heroVideo.removeAttribute("autoplay");
      heroVideo.pause();
    } else {
      tryPlay(heroVideo);
    }
  }

  var lazyVids = document.querySelectorAll("video[data-autoplay]");
  if (lazyVids.length && !reduceMotion) {
    if ("IntersectionObserver" in window) {
      var vio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) tryPlay(en.target);
          else en.target.pause();
        });
      }, { threshold: 0.25 });
      lazyVids.forEach(function (v) { vio.observe(v); });
    } else {
      lazyVids.forEach(tryPlay);
    }
  }

  /* Contact form: populate the topic dropdown from live collections */
  var topicSelect = document.querySelector("#fTopic[data-topics]");
  if (topicSelect) {
    fetchCatalog().then(function (cat) {
      cat.collections.slice().reverse().forEach(function (c) {
        /* only list collections that actually have products */
        if (!itemsFor(cat, c.slug).length) return;
        var o = document.createElement("option");
        o.textContent = c.label;
        topicSelect.insertBefore(o, topicSelect.firstChild);
      });
      topicSelect.selectedIndex = 0;
    }).catch(function () {});
  }

  /* Contact form → WhatsApp */
  var form = document.getElementById("waForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = document.getElementById("fName").value.trim();
      var topic = document.getElementById("fTopic").value;
      var msg = document.getElementById("fMsg").value.trim();
      var text =
        "Hello House of Naqash, my name is " + name + ". " +
        "I'm interested in: " + topic + "." + (msg ? "\n\n" + msg : "");
      window.open(
        "https://wa.me/919419014030?text=" + encodeURIComponent(text),
        "_blank", "noopener"
      );
    });
  }
})();
