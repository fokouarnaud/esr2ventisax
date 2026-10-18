// Note rapide (A29) : position GPS, brouillon local, aperçu des photos, envoi unique.
(function () {
  "use strict";

  var form = document.getElementById("note-rapide");
  if (!form) return;

  // --- Changement de stage : envoi immédiat (le bouton reste pour les navigateurs sans JS) ----------
  var choixStage = document.getElementById("choix-stage");
  if (choixStage) {
    choixStage.addEventListener("change", function () { choixStage.form.submit(); });
    var boutonStage = choixStage.form.querySelector("button");
    if (boutonStage) boutonStage.hidden = true;
  }

  // --- Brouillon (A6) : survit à un rechargement ou à une coupure réseau ---------------------------
  var cle = "carnet-brouillon-" + form.dataset.stage;
  var texte = form.querySelector("textarea[name=texte]");

  function lire() {
    try { return JSON.parse(localStorage.getItem(cle) || "null"); } catch (e) { return null; }
  }
  function ecrire() {
    var coches = Array.prototype.map.call(form.querySelectorAll("input[name=rubriques]:checked"), function (c) { return c.value; });
    try { localStorage.setItem(cle, JSON.stringify({ texte: texte.value, rubriques: coches })); } catch (e) { /* stockage indisponible */ }
  }
  function effacer() {
    try { localStorage.removeItem(cle); } catch (e) { /* rien */ }
  }

  if (form.dataset.enregistree === "1") {
    effacer();
  } else {
    var brouillon = lire();
    if (brouillon && !texte.value) {
      texte.value = brouillon.texte || "";
      (brouillon.rubriques || []).forEach(function (v) {
        var c = form.querySelector("input[name=rubriques][value='" + v + "']");
        if (c) c.checked = true;
      });
      var info = document.getElementById("brouillon-restaure");
      if (info && texte.value) info.hidden = false;
    }
  }
  form.addEventListener("input", ecrire);
  form.addEventListener("change", ecrire);

  // --- Position GPS ---------------------------------------------------------------------------------
  var etatGps = document.getElementById("etat-gps");
  var lat = form.querySelector("input[name=latitude]");
  var lon = form.querySelector("input[name=longitude]");

  function afficherGps(classe, icone, message, reessayer) {
    etatGps.className = "etat " + classe;
    etatGps.innerHTML = "";
    var i = document.createElement("span");
    i.className = "icone";
    i.setAttribute("aria-hidden", "true");
    i.textContent = icone;
    etatGps.appendChild(i);
    etatGps.appendChild(document.createTextNode(" " + message));
    if (reessayer) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = "Réessayer";
      b.addEventListener("click", localiser);
      etatGps.appendChild(document.createTextNode(" "));
      etatGps.appendChild(b);
    }
  }

  function localiser() {
    if (!("geolocation" in navigator)) {
      afficherGps("etat--alerte", "location_off", "Position non disponible sur cet appareil", false);
      return;
    }
    afficherGps("", "my_location", "Recherche de la position…", false);
    navigator.geolocation.getCurrentPosition(function (p) {
      lat.value = p.coords.latitude.toFixed(6);
      lon.value = p.coords.longitude.toFixed(6);
      afficherGps("etat--ok", "location_on", "Position captée (± " + Math.round(p.coords.accuracy) + " m)", false);
    }, function (err) {
      var refus = err.code === err.PERMISSION_DENIED;
      afficherGps("etat--alerte", "location_off", refus ? "Position refusée" : "Position introuvable", !refus);
    }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 });
  }
  if (etatGps) localiser();

  // --- Aperçu des photos -------------------------------------------------------------------------------
  var vignettes = document.getElementById("vignettes");
  var entrees = form.querySelectorAll("input[type=file][name=photos]");
  function apercu() {
    vignettes.innerHTML = "";
    var total = 0;
    Array.prototype.forEach.call(entrees, function (entree) {
      Array.prototype.forEach.call(entree.files, function (f) {
        total += 1;
        var img = document.createElement("img");
        img.alt = f.name;
        img.src = URL.createObjectURL(f);
        img.onload = function () { URL.revokeObjectURL(img.src); };
        vignettes.appendChild(img);
      });
    });
    var compte = document.getElementById("compte-photos");
    if (compte) compte.textContent = total ? total + " photo" + (total > 1 ? "s" : "") + " à envoyer" : "";
  }
  Array.prototype.forEach.call(entrees, function (e) { e.addEventListener("change", apercu); });

  // --- Envoi unique ---------------------------------------------------------------------------------
  form.addEventListener("submit", function () {
    var b = form.querySelector("button[type=submit]");
    b.disabled = true;
    b.lastChild.textContent = " Enregistrement…";
  });
})();
