"""Plans de situation (A31). Exécuté en local uniquement : la liste blanche de PythonAnywhere bloquerait les tuiles."""

from PIL import ImageDraw

URL_TUILES_OSM = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
LARGEUR, HAUTEUR, ZOOM = 800, 500, 16
MARINE, TURQUOISE = "#0b2d46", "#68ddce"


def generer_plan_situation(latitude, longitude, sortie, url_tuiles=URL_TUILES_OSM):
    from staticmap import CircleMarker, StaticMap

    carte = StaticMap(LARGEUR, HAUTEUR, url_template=url_tuiles,
                      headers={"User-Agent": "carnet-de-stage/1.0 (rapport de stage, usage ponctuel)"})
    carte.add_marker(CircleMarker((longitude, latitude), MARINE, 22))
    carte.add_marker(CircleMarker((longitude, latitude), TURQUOISE, 10))
    image = carte.render(zoom=ZOOM)
    dessin = ImageDraw.Draw(image)
    mention = "© OpenStreetMap contributors"
    gauche, haut, droite, bas = dessin.textbbox((0, 0), mention)
    x, y = LARGEUR - (droite - gauche) - 8, HAUTEUR - (bas - haut) - 8
    dessin.rectangle((x - 4, y - 3, LARGEUR, HAUTEUR), fill="white")
    dessin.text((x, y), mention, fill=MARINE)
    image.save(sortie)
