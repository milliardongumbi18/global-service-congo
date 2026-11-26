/* Global Service Congo : interactions de l'interface.
   Aucune donnée n'est envoyée : tout se passe dans le navigateur. */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* 1. Thème sombre / clair */
  var metaTheme = document.querySelector('meta[name="theme-color"]');

  function applyTheme(theme) {
    root.dataset.theme = theme;
    if (metaTheme) {
      metaTheme.setAttribute("content", theme === "light" ? "#f3f6fd" : "#050a18");
    }
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-label", theme === "light" ? "Passer au thème sombre" : "Passer au thème clair");
    });
  }

  applyTheme(root.dataset.theme === "light" ? "light" : "dark");

  document.addEventListener("click", function (event) {
    if (!event.target.closest("[data-theme-toggle]")) return;
    var next = root.dataset.theme === "light" ? "dark" : "light";
    root.classList.add("theme-anim");
    applyTheme(next);
    try { localStorage.setItem("gsc-theme", next); } catch (e) { /* stockage indisponible */ }
    window.setTimeout(function () { root.classList.remove("theme-anim"); }, 550);
  });

  /* 2. Menu mobile */
  var menuBtn = document.querySelector("[data-menu-toggle]");
  var menu = document.getElementById("menu-mobile");
  if (menuBtn && menu) {
    menuBtn.addEventListener("click", function () {
      var open = !menu.classList.toggle("hidden");
      menuBtn.setAttribute("aria-expanded", String(open));
      menuBtn.setAttribute("aria-label", open ? "Fermer le menu" : "Ouvrir le menu");
    });
  }

  /* 3. En-tête qui passe en verre dépoli au défilement */
  var header = document.querySelector("[data-header]");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* 4. Lueur qui suit la souris ou le doigt sur les cartes .spot */
  var spotFrame = null;
  document.addEventListener("pointermove", function (event) {
    var card = event.target.closest ? event.target.closest(".spot") : null;
    if (!card) return;
    if (spotFrame) cancelAnimationFrame(spotFrame);
    spotFrame = requestAnimationFrame(function () {
      var box = card.getBoundingClientRect();
      card.style.setProperty("--mx", (event.clientX - box.left) + "px");
      card.style.setProperty("--my", (event.clientY - box.top) + "px");
    });
  }, { passive: true });

  /* 5. Effet 3D du visuel (ordinateur uniquement, et seulement si les animations sont autorisées) */
  if (finePointer && !reduceMotion) {
    document.querySelectorAll("[data-tilt]").forEach(function (el) {
      var frame = null;
      el.addEventListener("pointermove", function (event) {
        if (frame) cancelAnimationFrame(frame);
        frame = requestAnimationFrame(function () {
          var box = el.getBoundingClientRect();
          el.style.setProperty("--px", ((event.clientX - box.left) / box.width - 0.5).toFixed(3));
          el.style.setProperty("--py", ((event.clientY - box.top) / box.height - 0.5).toFixed(3));
        });
      });
      el.addEventListener("pointerleave", function () {
        el.style.setProperty("--px", "0");
        el.style.setProperty("--py", "0");
      });
    });
  }

  /* 6. Apparition douce des sections au défilement */
  var reveals = document.querySelectorAll(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    reveals.forEach(function (node) { node.classList.add("is-in"); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -10% 0px" });
    reveals.forEach(function (node) { revealObserver.observe(node); });
  }
})();