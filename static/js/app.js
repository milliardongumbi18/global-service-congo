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

  /* 7. Afficher / masquer le mot de passe (tous les champs mot de passe du même formulaire) */
  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-password-toggle]");
    if (!btn) return;
    var form = btn.closest("form");
    var show = !btn.classList.contains("is-visible");
    form.querySelectorAll("input[type=password], input[data-was-password]").forEach(function (input) {
      input.setAttribute("data-was-password", "1");
      input.type = show ? "text" : "password";
    });
    form.querySelectorAll("[data-password-toggle]").forEach(function (b) {
      b.classList.toggle("is-visible", show);
      b.setAttribute("aria-label", show ? "Masquer le mot de passe" : "Afficher le mot de passe");
    });
  });

  /* 8. Indicateur de force du mot de passe (indicatif : le serveur reste seul juge) */
  document.querySelectorAll("[data-strength-for]").forEach(function (meter) {
    var input = document.getElementById(meter.getAttribute("data-strength-for"));
    if (!input) return;
    var bars = meter.querySelectorAll(".strength-bars i");
    var label = meter.querySelector("[data-strength-label]");
    var labels = ["Très faible", "Faible", "Moyen", "Bon", "Fort", "Très fort"];
    function update() {
      var v = input.value;
      var checks = {
        length: v.length >= 10,
        mixed: /[a-z]/.test(v) && /[A-Z]/.test(v),
        digit: /\d/.test(v),
        special: /[^A-Za-z0-9]/.test(v)
      };
      var score = 0;
      Object.keys(checks).forEach(function (key) {
        if (checks[key]) score++;
        var hint = meter.querySelector('[data-hint="' + key + '"]');
        if (hint) hint.classList.toggle("is-ok", checks[key]);
      });
      if (v.length >= 14) score++;
      bars.forEach(function (bar, i) { bar.classList.toggle("is-on", i < score); });
      meter.dataset.level = score <= 2 ? "low" : (score === 3 ? "mid" : "high");
      if (label) label.textContent = v ? labels[score] : "—";
    }
    input.addEventListener("input", update);
    update();
  });

  /* 9. Formulaire en étapes (sans JavaScript, toutes les étapes s'affichent à la suite) */
  document.querySelectorAll("[data-stepper]").forEach(function (form) {
    var panels = Array.prototype.slice.call(form.querySelectorAll("[data-step-panel]"));
    if (panels.length < 2) return;
    var scope = form.closest("[data-stepper-scope]") || document;
    var indicators = scope.querySelectorAll("[data-step-indicator]");
    var current = 0;
    var started = false;

    form.classList.add("is-stepper");
    form.noValidate = true; // on valide nous-mêmes, étape par étape

    function show(index) {
      current = Math.max(0, Math.min(index, panels.length - 1));
      panels.forEach(function (p, i) { p.classList.toggle("is-active", i === current); });
      indicators.forEach(function (ind, i) {
        ind.classList.toggle("is-active", i === current);
        ind.classList.toggle("is-done", i < current);
      });
      if (started) {
        var first = panels[current].querySelector("input:not([type=hidden]):not([type=checkbox]), select");
        if (first) first.focus({ preventScroll: true });
        scope.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
      }
    }

    function firstInvalid(panel) {
      var fields = panel.querySelectorAll("input, select, textarea");
      for (var i = 0; i < fields.length; i++) {
        if (!fields[i].checkValidity()) return fields[i];
      }
      return null;
    }

    form.addEventListener("click", function (event) {
      if (event.target.closest("[data-step-next]")) {
        event.preventDefault();
        var bad = firstInvalid(panels[current]);
        if (bad) { bad.reportValidity(); return; }
        show(current + 1);
      } else if (event.target.closest("[data-step-prev]")) {
        event.preventDefault();
        show(current - 1);
      }
    });

    // À l'envoi : si un champ d'une étape est invalide, on ouvre cette étape
    form.addEventListener("submit", function (event) {
      for (var i = 0; i < panels.length; i++) {
        var bad = firstInvalid(panels[i]);
        if (bad) {
          event.preventDefault();
          show(i);
          bad.reportValidity();
          return;
        }
      }
    });

    // Après une erreur du serveur : on rouvre l'étape qui contient la première erreur
    var start = 0;
    var error = form.querySelector(".field-error");
    if (error && error.closest("[data-step-panel]")) {
      start = panels.indexOf(error.closest("[data-step-panel]"));
    }
    show(start);
    started = true;
  });

  /* 10. Bouton « en cours… » : évite les doubles envois */
  document.addEventListener("submit", function (event) {
    if (event.defaultPrevented) return;
    var btn = event.target.querySelector("[data-loading-text]");
    if (!btn) return;
    btn.textContent = btn.getAttribute("data-loading-text");
    btn.setAttribute("aria-disabled", "true");
    btn.classList.add("is-loading");
  });
})();