// Saisie d'un lieu : valeur sans signe + hémisphère (N/S, E/O), position du téléphone ou coordonnées collées.
(function () {
  function champs(axe) {
    var bloc = document.querySelector('.saisie-coordonnee[data-axe="' + axe + '"]');
    return bloc ? { valeur: bloc.querySelector("input"), sens: bloc.querySelector("select") } : null;
  }

  function remplir(axe, nombre) {
    var c = champs(axe);
    if (!c) return;
    var negatif = axe === "latitude" ? "S" : "O";
    var positif = axe === "latitude" ? "N" : "E";
    c.valeur.value = Math.abs(nombre).toFixed(6).replace(".", ",");
    c.sens.value = nombre < 0 ? negatif : positif;
    c.valeur.dispatchEvent(new Event("change", { bubbles: true }));
  }

  document.addEventListener("DOMContentLoaded", function () {
    var lat = champs("latitude");
    if (!lat) return;

    // Coller « 4.0496, 9.6942 » (OpenStreetMap, Google Maps) remplit latitude et longitude.
    lat.valeur.addEventListener("paste", function (e) {
      var texte = (e.clipboardData || window.clipboardData).getData("text");
      var m = texte.match(/(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)/);
      if (!m) return;
      e.preventDefault();
      remplir("latitude", parseFloat(m[1]));
      remplir("longitude", parseFloat(m[2]));
    });

    var bouton = document.querySelector("[data-ma-position]");
    var etat = document.querySelector("[data-etat-position]");
    if (!bouton) return;
    if (!("geolocation" in navigator)) {
      bouton.hidden = true;
      return;
    }
    bouton.addEventListener("click", function () {
      etat.textContent = "Recherche de la position…";
      navigator.geolocation.getCurrentPosition(function (p) {
        remplir("latitude", p.coords.latitude);
        remplir("longitude", p.coords.longitude);
        etat.textContent = "Position captée (± " + Math.round(p.coords.accuracy) + " m). Vérifiez-la, puis enregistrez.";
      }, function (err) {
        etat.textContent = err.code === 1
          ? "Localisation refusée : autorisez-la dans le navigateur, ou copiez la position depuis une carte."
          : "Position introuvable : réessayez à l'extérieur, ou copiez la position depuis une carte.";
      }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 });
    });
  });
})();
