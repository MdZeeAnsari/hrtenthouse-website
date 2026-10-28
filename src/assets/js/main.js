/* H.R. Tent House & Caterers — site motion + behaviour.
   Everything here only enhances: every page reads complete with JS off. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement, body = doc.body;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var hasGsap = typeof window.gsap !== "undefined";
  var cfg = window.HRTH || {};

  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }
  function ss(k, v) { try { if (v === undefined) return sessionStorage.getItem(k); sessionStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---------- intro: click to skip ---------- */
  var intro = $(".intro-overlay");
  if (intro) {
    intro.addEventListener("click", function () { root.classList.add("intro-done"); });
    setTimeout(function () { root.classList.add("intro-done"); }, 2000);
  }

  /* ---------- header + mobile menu ---------- */
  var header = $(".site-header");
  function onScrollHeader() { if (header) header.classList.toggle("is-scrolled", window.scrollY > 40); }
  onScrollHeader();
  window.addEventListener("scroll", onScrollHeader, { passive: true });

  var menuBtn = $(".menu-btn");
  function setMenu(open) {
    body.classList.toggle("menu-open", open);
    if (menuBtn) menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    var m = $("#mobile-menu"); if (m) m.setAttribute("aria-hidden", open ? "false" : "true");
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () { setMenu(!body.classList.contains("menu-open")); });
    doc.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
    $$("#mobile-menu a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
  }

  /* ---------- page-change drapes ---------- */
  var curtain = $(".curtain");
  function isInternal(a) {
    if (!a || !a.href || a.target === "_blank" || a.hasAttribute("download") || a.dataset.noCurtain !== undefined) return false;
    if (a.protocol !== location.protocol || a.host !== location.host) return false;
    if (a.pathname === location.pathname && a.hash) return false;
    return /\.html?$|\/$/.test(a.pathname);
  }
  if (curtain && !reduce) {
    doc.addEventListener("click", function (e) {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var a = e.target.closest && e.target.closest("a");
      if (!isInternal(a)) return;
      if (a.pathname === location.pathname && !a.hash) return;
      e.preventDefault();
      var label = a.dataset.label || a.getAttribute("aria-label") || a.textContent.trim().replace(/\s+/g, " ").slice(0, 28) || "Home";
      $(".curtain__tag span", curtain).textContent = label;
      ss("hrth-drape", label);
      curtain.classList.add("is-closing");
      setTimeout(function () { location.href = a.href; }, 460);
    });
    window.addEventListener("pageshow", function (e) { if (e.persisted) { curtain.classList.remove("is-closing"); root.classList.remove("drape-in"); } });
  }

  /* ---------- year ---------- */
  $$("[data-year]").forEach(function (n) { n.textContent = new Date().getFullYear(); });

  /* ---------- floating dock: sliding pill ---------- */
  var dock = $(".dock");
  if (dock) {
    var pill = $(".dock__pill", dock);
    var active = $("a.is-active", dock);
    var place = function (el) {
      if (!el) { dock.classList.remove("has-pill"); return; }
      dock.classList.add("has-pill");
      var x = el.offsetLeft, w = el.offsetWidth;
      if (hasGsap && !reduce) gsap.to(pill, { x: x, width: w, duration: .55, ease: "elastic.out(1, .75)" });
      else { pill.style.transform = "translateX(" + x + "px)"; pill.style.width = w + "px"; }
    };
    if (active) { pill.style.transform = "translateX(" + active.offsetLeft + "px)"; pill.style.width = active.offsetWidth + "px"; dock.classList.add("has-pill"); }
    if (finePointer) {
      $$("a", dock).forEach(function (a) {
        a.addEventListener("mouseenter", function () { $$("a", dock).forEach(function (b) { b.classList.toggle("is-active", b === a); }); place(a); });
      });
      dock.addEventListener("mouseleave", function () {
        $$("a", dock).forEach(function (b) { b.classList.toggle("is-active", b === active); }); place(active);
      });
    }
    window.addEventListener("resize", function () { if (active) place(active); });
  }

  /* ---------- custom lamp cursor ---------- */
  if (finePointer && !reduce) {
    var dot = doc.createElement("div"), ring = doc.createElement("div");
    dot.className = "cursor-dot"; ring.className = "cursor-ring";
    body.appendChild(dot); body.appendChild(ring);
    var mx = -100, my = -100, rx = -100, ry = -100, shown = false;
    doc.addEventListener("pointermove", function (e) {
      mx = e.clientX; my = e.clientY;
      if (!shown) { shown = true; rx = mx; ry = my; root.classList.add("has-cursor"); }
      dot.style.transform = "translate(" + mx + "px," + my + "px)";
    }, { passive: true });
    doc.addEventListener("pointerleave", function () { root.classList.remove("has-cursor"); shown = false; });
    (function loop() {
      rx += (mx - rx) * .18; ry += (my - ry) * .18;
      ring.style.transform = "translate(" + rx + "px," + ry + "px)";
      requestAnimationFrame(loop);
    })();
    doc.addEventListener("pointerover", function (e) {
      var t = e.target.closest && e.target.closest("a,button,summary,select,input,textarea,label");
      ring.classList.toggle("is-big", !!t);
    });
  }

  /* ---------- string of lights reacts to the cursor ---------- */
  var lights = $(".lights");
  if (lights && finePointer && !reduce) {
    var bulbs = $$(".bulb", lights), raf = 0, px = -9999, py = -9999;
    var hero = lights.closest(".hero");
    var update = function () {
      raf = 0;
      bulbs.forEach(function (b) {
        var r = b.getBoundingClientRect();
        var d = Math.hypot(r.left + r.width / 2 - px, r.top + r.height / 2 - py);
        b.style.setProperty("--near", Math.max(0, 1 - d / 260).toFixed(2));
      });
    };
    hero.addEventListener("pointermove", function (e) { px = e.clientX; py = e.clientY; if (!raf) raf = requestAnimationFrame(update); });
    hero.addEventListener("pointerleave", function () { px = py = -9999; if (!raf) raf = requestAnimationFrame(update); });
  }

  /* ---------- bokeh light particles (hero + footer), paused off screen ---------- */
  if (!reduce) {
    $$("canvas.bokeh").forEach(function (cv) {
      var ctx = cv.getContext("2d"); if (!ctx) return;
      var dpr = Math.min(window.devicePixelRatio || 1, 2), W = 0, H = 0, parts = [], running = false, id = 0;
      var count = window.innerWidth < 700 ? 9 : 16;
      function size() {
        W = cv.clientWidth; H = cv.clientHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }
      function make() {
        parts = [];
        for (var i = 0; i < count; i++) parts.push({
          x: Math.random() * W, y: Math.random() * H, r: 8 + Math.random() * 34,
          vx: (Math.random() - .5) * .12, vy: -.05 - Math.random() * .16, a: .05 + Math.random() * .16, t: Math.random() * 6.28
        });
      }
      function frame() {
        ctx.clearRect(0, 0, W, H);
        for (var i = 0; i < parts.length; i++) {
          var p = parts[i]; p.x += p.vx; p.y += p.vy; p.t += .01;
          if (p.y < -p.r) { p.y = H + p.r; p.x = Math.random() * W; }
          if (p.x < -p.r) p.x = W + p.r; if (p.x > W + p.r) p.x = -p.r;
          var g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r);
          var al = p.a * (.75 + .25 * Math.sin(p.t));
          g.addColorStop(0, "rgba(255,226,170," + al + ")"); g.addColorStop(1, "rgba(255,226,170,0)");
          ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill();
        }
        if (running) id = requestAnimationFrame(frame);
      }
      size(); make();
      window.addEventListener("resize", function () { size(); });
      new IntersectionObserver(function (en) {
        var vis = en[0].isIntersecting;
        if (vis && !running) { running = true; id = requestAnimationFrame(frame); }
        else if (!vis && running) { running = false; cancelAnimationFrame(id); }
      }).observe(cv);
    });
  }

  /* ---------- gallery teaser: 3D tilt + glow ---------- */
  $$(".teaser").forEach(function (card) {
    var glow = $(".teaser__glow", card);
    card.addEventListener("pointermove", function (e) {
      var r = card.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      card.style.setProperty("--gx", (x * 100) + "%"); card.style.setProperty("--gy", (y * 100) + "%");
      if (!finePointer || reduce || !hasGsap) return;
      gsap.to(card, { rotateY: (x - .5) * 8, rotateX: (.5 - y) * 6, transformPerspective: 1100, duration: .8, ease: "elastic.out(1,.6)" });
    });
    card.addEventListener("pointerleave", function () {
      if (hasGsap) gsap.to(card, { rotateY: 0, rotateX: 0, duration: 1, ease: "elastic.out(1,.5)" });
    });
    if (glow) glow.setAttribute("aria-hidden", "true");
  });

  /* ---------- diya loader helper ---------- */
  var diyaCaps = ["Lighting the lamps…", "Setting the stage…", "Almost ready…"];
  function diya(el) {
    var cap = $(".diya__cap", el), i = 0, timer = 0, shownAt = 0, delay = 0;
    return {
      start: function () {
        clearTimeout(delay);
        delay = setTimeout(function () {
          el.classList.add("is-on"); shownAt = Date.now(); i = 0; if (cap) cap.textContent = diyaCaps[0];
          timer = setInterval(function () { i = Math.min(i + 1, diyaCaps.length - 1); if (cap) cap.textContent = diyaCaps[i]; }, 450);
        }, 150);
      },
      stop: function () { clearTimeout(delay); clearInterval(timer); el.classList.remove("is-on"); }
    };
  }

  /* ---------- gallery: filter + lightbox ---------- */
  var masonry = $(".masonry");
  if (masonry) {
    var tiles = $$(".tile", masonry);
    $$(".filter").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var f = btn.dataset.filter;
        $$(".filter").forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
        var state = (hasGsap && window.Flip && !reduce) ? Flip.getState(tiles) : null;
        tiles.forEach(function (t) { t.classList.toggle("is-hidden", f !== "all" && t.dataset.cat.split(" ").indexOf(f) < 0); });
        if (state) Flip.from(state, { duration: .5, ease: "power3.inOut", absolute: true, scale: true,
          onEnter: function (els) { return gsap.fromTo(els, { opacity: 0, scale: .92 }, { opacity: 1, scale: 1, duration: .45 }); },
          onLeave: function (els) { return gsap.to(els, { opacity: 0, scale: .92, duration: .3 }); } });
        if (window.ScrollTrigger) setTimeout(function () { ScrollTrigger.refresh(); }, 520);
      });
    });

    var lb = $(".lightbox"), lbImg = $(".lightbox__img", lb), lbCap = $(".lightbox__cap", lb), loader = diya($(".diya", lb));
    var list = [], idx = 0, lastFocus = null;
    function visibleTiles() { return tiles.filter(function (t) { return !t.classList.contains("is-hidden"); }); }
    function show(i) {
      idx = (i + list.length) % list.length;
      var b = $("button", list[idx]);
      lbImg.classList.add("is-loading"); loader.start();
      var img = new Image();
      img.onload = img.onerror = function () { lbImg.src = img.src; lbImg.alt = b.dataset.alt; lbImg.classList.remove("is-loading"); loader.stop(); };
      img.src = b.dataset.full;
      lbCap.textContent = b.dataset.alt + "  ·  " + (idx + 1) + " / " + list.length;
    }
    function open(t) {
      list = visibleTiles(); lastFocus = doc.activeElement;
      lb.classList.add("is-open"); root.style.overflow = "hidden"; if (window.__lenis) window.__lenis.stop();
      show(list.indexOf(t)); $(".lb-close", lb).focus();
    }
    function close() {
      lb.classList.remove("is-open"); root.style.overflow = ""; if (window.__lenis) window.__lenis.start(); lbImg.removeAttribute("src");
      if (lastFocus) lastFocus.focus();
    }
    tiles.forEach(function (t) { $("button", t).addEventListener("click", function () { open(t); }); });
    $(".lb-close", lb).addEventListener("click", close);
    $(".lb-prev", lb).addEventListener("click", function () { show(idx - 1); });
    $(".lb-next", lb).addEventListener("click", function () { show(idx + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    doc.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
      if (e.key === "Escape") close(); else if (e.key === "ArrowLeft") show(idx - 1); else if (e.key === "ArrowRight") show(idx + 1);
    });
    var sx = 0, sy = 0;
    lb.addEventListener("pointerdown", function (e) { sx = e.clientX; sy = e.clientY; });
    lb.addEventListener("pointerup", function (e) {
      var dx = e.clientX - sx, dy = e.clientY - sy;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(idx + (dx < 0 ? 1 : -1));
    });
  }

  /* ---------- enquiry form ---------- */
  $$("form.enquiry-form").forEach(function (form) {
    var status = $(".form__status", form), btn = $("button[type=submit]", form), loader = diya($(".diya", form));
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var d = new FormData(form);
      if (d.get("botcheck")) return;
      var lines = [
        "Hi H.R. Tent House, I'd like a quote.",
        "Name: " + d.get("name"), "Phone: " + d.get("phone"),
        d.get("event_type") ? "Event: " + d.get("event_type") : "",
        d.get("event_date") ? "Date: " + d.get("event_date") : "",
        d.get("guests") ? "Guests: " + d.get("guests") : "",
        d.get("venue") ? "Venue/area: " + d.get("venue") : "",
        d.get("message") ? "Details: " + d.get("message") : ""
      ].filter(Boolean).join("\n");
      var waUrl = "https://wa.me/" + (cfg.whatsapp || "919902020244") + "?text=" + encodeURIComponent(lines);
      var key = cfg.web3formsKey || "";
      function setStatus(ok, html) { status.className = "form__status " + (ok ? "is-ok" : "is-err"); status.innerHTML = html; }

      if (!key || key.indexOf("YOUR_") === 0) {
        // No email service set up yet: send the enquiry on WhatsApp instead.
        var w = window.open(waUrl, "_blank");
        if (w) { try { w.opener = null; } catch (x) {} } else { location.href = waUrl; }
        setStatus(true, "WhatsApp opened with your enquiry. Just press send. If it didn't open, <a href=\"" + waUrl + "\" target=\"_blank\" rel=\"noopener\">tap here</a>.");
        return;
      }
      btn.disabled = true; loader.start();
      d.append("access_key", key);
      d.append("subject", "New quote request from " + d.get("name") + " (website)");
      d.append("from_name", "H.R. Tent House website");
      fetch("https://api.web3forms.com/submit", { method: "POST", body: d, headers: { Accept: "application/json" } })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j && j.success) { form.reset(); setStatus(true, "Thank you! We've received your enquiry and will call you back shortly. For a faster reply, <a href=\"" + waUrl + "\" target=\"_blank\" rel=\"noopener\">WhatsApp us</a>."); }
          else throw new Error("fail");
        })
        .catch(function () { setStatus(false, "Sorry, that didn't go through. Please <a href=\"" + waUrl + "\" target=\"_blank\" rel=\"noopener\">send it on WhatsApp</a> or call <a href=\"tel:+919902020244\">99020 20244</a>."); })
        .then(function () { btn.disabled = false; loader.stop(); });
    });
  });

  /* ====================== GSAP-driven motion ====================== */
  if (!hasGsap) return;
  if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);
  if (window.Flip) gsap.registerPlugin(Flip);
  var EASE = "cubic-bezier(.16,1,.3,1)";
  if (gsap.parseEase) { try { gsap.registerEase("hrth", function (p) { return 1 - Math.pow(1 - p, 4); }); EASE = "hrth"; } catch (e) {} }

  /* smooth scroll: desktop only */
  if (window.Lenis && finePointer && !reduce && window.innerWidth >= 1024) {
    var lenis = new Lenis({ duration: 1.1, smoothWheel: true, anchors: { offset: -90 } });
    window.__lenis = lenis;
    if (window.ScrollTrigger) lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
  }

  if (!window.ScrollTrigger) return;

  if (reduce) {
    // simple fades only
    $$("[data-reveal],[data-reveal-stagger]>*").forEach(function (el) {
      gsap.from(el, { opacity: 0, duration: .4, scrollTrigger: { trigger: el, start: "top 90%", once: true } });
    });
    return;
  }

  /* section reveals: fade + rise, stagger children, image clip-reveal */
  $$("[data-reveal]").forEach(function (el) {
    gsap.from(el, { y: 36, opacity: 0, duration: .8, ease: EASE, scrollTrigger: { trigger: el, start: "top 80%", once: true } });
  });
  $$("[data-reveal-stagger]").forEach(function (wrap) {
    gsap.from(wrap.children, { y: 36, opacity: 0, duration: .8, ease: EASE, stagger: .06, scrollTrigger: { trigger: wrap, start: "top 80%", once: true } });
  });
  $$("[data-clip]").forEach(function (el) {
    gsap.fromTo(el, { clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.1, ease: EASE, scrollTrigger: { trigger: el, start: "top 85%", once: true } });
  });

  /* hero parallax: photo moves slower than the text */
  var hm = $(".hero__media");
  if (hm) gsap.to(hm, { yPercent: 14, ease: "none", scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true } });
  var pm = $(".page-hero__media");
  if (pm) gsap.to(pm, { yPercent: 18, ease: "none", scrollTrigger: { trigger: ".page-hero", start: "top top", end: "bottom top", scrub: true } });

  /* how-we-work timeline */
  var steps = $(".steps");
  if (steps) {
    var fill = $(".steps__fill", steps), items = $$(".step", steps), imgs = $$(".steps__panel img", steps);
    gsap.fromTo(fill, { scaleY: 0 }, { scaleY: 1, ease: "none", scrollTrigger: { trigger: ".steps__list", start: "top 65%", end: "bottom 55%", scrub: .4 } });
    items.forEach(function (it, i) {
      ScrollTrigger.create({ trigger: it, start: "top 60%", end: "bottom 60%",
        onToggle: function (s) {
          if (!s.isActive) return;
          items.forEach(function (o, j) { o.classList.toggle("is-active", j === i); });
          imgs.forEach(function (o, j) { o.classList.toggle("is-active", j === i); });
        } });
    });
  }

  /* count-up numbers */
  $$("[data-count]").forEach(function (el) {
    var to = parseFloat(el.dataset.count), from = parseFloat(el.dataset.from || 0), o = { v: from };
    var sup = $("sup", el), supHTML = sup ? sup.outerHTML : "";
    gsap.to(o, { v: to, duration: 1.2, ease: "power2.out", scrollTrigger: { trigger: el, start: "top 85%", once: true },
      onUpdate: function () { el.innerHTML = Math.round(o.v) + supHTML; } });
  });

  /* refresh once images/fonts settle */
  window.addEventListener("load", function () { ScrollTrigger.refresh(); });
})();
