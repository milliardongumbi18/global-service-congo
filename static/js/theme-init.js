/* Chargé dans <head>, AVANT l'affichage : applique le thème mémorisé pour éviter un flash clair/sombre. */
(function () {
  var root = document.documentElement;
  root.classList.add("js");
  try {
    var saved = localStorage.getItem("gsc-theme");
    if (saved === "light" || saved === "dark") {
      root.dataset.theme = saved;
    }
  } catch (e) {
    /* Navigation privée : on garde le thème sombre par défaut. */
  }
})();