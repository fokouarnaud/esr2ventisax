"""Construit la présentation de soutenance FeatherFace ECA-CBAM (contenu tiré du mémoire)."""
from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
ACCENT = RGBColor(0xE0, 0x7A, 0x1F)
LIGHT = RGBColor(0xF2, 0xF5, 0xF9)
GREY = RGBColor(0x5B, 0x67, 0x70)
TEXT = RGBColor(0x22, 0x2B, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Calibri"

AUTHOR = "FOKOU Arnaud Cedric"
SECTIONS = ["Contexte", "État de l'art", "Méthodologie", "Résultats", "Conclusion"]

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
slides_meta: list = []


def style_run(run, size, bold=False, color=TEXT, italic=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def textbox(slide, x, y, w, h, text, size=18, bold=False, color=TEXT, align=PP_ALIGN.LEFT,
            anchor=MSO_ANCHOR.TOP, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        style_run(p.add_run(), size, bold, color, italic)
        p.runs[0].text = line
    return box


def bullets(slide, x, y, w, h, items, size=18, color=TEXT, gap=8):
    """items : str ou (texte_gras, suite)."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        style_run(p.add_run(), size, True, ACCENT)
        p.runs[0].text = "▪  "
        if isinstance(item, tuple):
            r = p.add_run(); style_run(r, size, True, NAVY); r.text = item[0]
            r = p.add_run(); style_run(r, size, False, color); r.text = item[1]
        else:
            r = p.add_run(); style_run(r, size, False, color); r.text = item
    return box


def rect(slide, x, y, w, h, fill=LIGHT, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(1.25)
    s.shadow.inherit = False
    return s


def card(slide, x, y, w, h, title, body, size=15, head=NAVY):
    rect(slide, x, y, w, h, LIGHT)
    rect(slide, x, y, w, 0.08, head)
    textbox(slide, x + 0.15, y + 0.18, w - 0.3, 0.45, title, 17, True, head)
    if isinstance(body, list):
        bullets(slide, x + 0.15, y + 0.68, w - 0.3, h - 0.8, body, size, gap=4)
    else:
        textbox(slide, x + 0.15, y + 0.68, w - 0.3, h - 0.8, body, size)


def metric(slide, x, y, w, value, label, color=ACCENT):
    rect(slide, x, y, w, 1.35, WHITE, line=color)
    textbox(slide, x, y + 0.08, w, 0.7, value, 32, True, color, PP_ALIGN.CENTER)
    textbox(slide, x + 0.1, y + 0.78, w - 0.2, 0.5, label, 13, False, GREY, PP_ALIGN.CENTER)


def table(slide, x, y, w, rows, col_w=None, size=14, highlight_last=False, row_h=0.42):
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    t = gt.table
    if col_w:
        for i, cw in enumerate(col_w):
            t.columns[i].width = Inches(cw)
    for r in range(nr):
        t.rows[r].height = Inches(row_h)
        for c in range(nc):
            cell = t.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            hl = highlight_last and r == nr - 1
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if r == 0 else (RGBColor(0xFD, 0xEB, 0xD9) if hl else (LIGHT if r % 2 else WHITE))
            tf = cell.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
            run = p.add_run()
            run.text = str(rows[r][c])
            style_run(run, size, r == 0 or hl, WHITE if r == 0 else (NAVY if hl else TEXT))
    return t


def bar_chart(slide, x, y, w, h, cats, series, title, number_format='0.0"%"', vmin=None, vmax=None,
              chart_type=XL_CHART_TYPE.COLUMN_CLUSTERED, colors=None, legend=True, point_colors=None):
    data = CategoryChartData()
    data.categories = cats
    for name, vals in series:
        data.add_series(name, vals)
    gf = slide.shapes.add_chart(chart_type, Inches(x), Inches(y), Inches(w), Inches(h), data)
    ch = gf.chart
    ch.has_title = True
    ch.chart_title.text_frame.text = title
    style_run(ch.chart_title.text_frame.paragraphs[0].runs[0], 15, True, NAVY)
    ch.has_legend = legend and len(series) > 1
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(12)
    va = ch.value_axis
    if vmin is not None: va.minimum_scale = vmin
    if vmax is not None: va.maximum_scale = vmax
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(0xDD, 0xE2, 0xE8)
    va.tick_labels.font.size = Pt(11)
    va.tick_labels.number_format = number_format
    va.tick_labels.number_format_is_linked = False
    ch.category_axis.tick_labels.font.size = Pt(12)
    palette = colors or [NAVY, ACCENT, GREY]
    plot = ch.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.font.size = Pt(11)
    dl.number_format = number_format
    dl.number_format_is_linked = False
    if chart_type in (XL_CHART_TYPE.COLUMN_CLUSTERED, XL_CHART_TYPE.BAR_CLUSTERED):
        plot.gap_width = 60
        dl.position = XL_LABEL_POSITION.OUTSIDE_END
    for i, s in enumerate(plot.series):
        color = palette[i % len(palette)]
        if chart_type == XL_CHART_TYPE.LINE_MARKERS:
            s.format.line.color.rgb = color
            s.format.line.width = Pt(3)
            s.smooth = False
            s.marker.format.fill.solid(); s.marker.format.fill.fore_color.rgb = color
            dl.position = XL_LABEL_POSITION.ABOVE
        else:
            s.format.fill.solid(); s.format.fill.fore_color.rgb = color
    if point_colors:
        for idx, color in point_colors.items():
            pt = plot.series[0].points[idx]
            pt.format.fill.solid(); pt.format.fill.fore_color.rgb = color
    return ch


def new_slide(title, section=None, notes=""):
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, 0.18, 7.5, NAVY)
    textbox(s, 0.55, 0.35, 10.6, 0.8, title, 30, True, NAVY, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, 0.6, 1.15, 1.2, 0.06, ACCENT)
    if section:
        # navigation : la section active est en couleur d'accent
        x = 0.6
        nav = s.shapes.add_textbox(Inches(8.2), Inches(0.12), Inches(4.9), Inches(0.3))
        p = nav.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
        for i, name in enumerate(SECTIONS):
            r = p.add_run(); r.text = name
            style_run(r, 10, name == section, ACCENT if name == section else GREY)
            if i < len(SECTIONS) - 1:
                r = p.add_run(); r.text = "  ·  "; style_run(r, 10, False, GREY)
    s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.6), Inches(6.95), Inches(12.9), Inches(6.95)).line.color.rgb = RGBColor(0xD0, 0xD6, 0xDE)
    textbox(s, 0.6, 7.0, 9, 0.35, f"{AUTHOR}  —  Soutenance de Master II en Informatique  —  UY1", 11, False, GREY)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    slides_meta.append(s)
    return s


def number_slides():
    total = len(prs.slides)
    for i, s in enumerate(prs.slides, 1):
        if i == 1:
            continue
        textbox(s, 11.9, 7.0, 1.0, 0.35, f"{i} / {total}", 11, True, NAVY, PP_ALIGN.RIGHT)


def flow_box(slide, x, y, w, h, text, fill, color=WHITE, size=13):
    b = rect(slide, x, y, w, h, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tf = b.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = line
        style_run(r, size if i == 0 else size - 2, i == 0, color)
    return b


def arrow(slide, x1, y1, x2, y2, color=GREY):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color; c.line.width = Pt(2)
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd", {"type": "triangle"})
    ln.append(tail)
    return c


# ---------------------------------------------------------------- 1. Couverture
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, 13.333, 7.5, NAVY)
rect(s, 0, 5.05, 13.333, 0.06, ACCENT)
logo = SRC / "img" / "logoUY1.png"
rect(s, 0.6, 0.45, 1.35, 1.35, WHITE, shape=MSO_SHAPE.OVAL)
s.shapes.add_picture(str(logo), Inches(0.72), Inches(0.57), Inches(1.11), Inches(1.11))
textbox(s, 2.15, 0.55, 8, 0.45, "UNIVERSITÉ DE YAOUNDÉ I", 18, True, WHITE)
textbox(s, 2.15, 1.0, 8, 0.4, "Département d'Informatique  ·  Mémoire de Master II", 15, False, RGBColor(0xC9, 0xD3, 0xE0))
textbox(s, 0.6, 2.15, 12.1, 1.9,
        "Détection faciale sur smartphone au moyen d'un mécanisme d'attention hybride ECA-CBAM",
        36, True, WHITE, anchor=MSO_ANCHOR.MIDDLE)
textbox(s, 0.6, 4.1, 12, 0.6, "Application à la vérification de présence en salle de classe", 20, False, ACCENT)
textbox(s, 0.6, 5.35, 6, 0.4, "Présenté par", 13, False, RGBColor(0xC9, 0xD3, 0xE0))
textbox(s, 0.6, 5.7, 6, 0.5, "FOKOU Arnaud Cedric  –  13Y180", 20, True, WHITE)
textbox(s, 7.2, 5.35, 5.5, 0.4, "Sous la direction de", 13, False, RGBColor(0xC9, 0xD3, 0xE0))
textbox(s, 7.2, 5.7, 5.5, 0.8, "Dr. AMINOU Halidou\nDr. Janvier NGNOULAYE", 18, True, WHITE)
textbox(s, 0.6, 6.75, 6, 0.4, "Année académique 2024 – 2025", 14, False, RGBColor(0xC9, 0xD3, 0xE0))
s.notes_slide.notes_text_frame.text = (
    "Bonjour. Je vous présente mon mémoire de Master II : la détection faciale sur smartphone "
    "par un mécanisme d'attention hybride ECA-CBAM, appliquée à la vérification de présence en salle de classe, "
    "sous la direction du Dr. AMINOU Halidou et du Dr. Janvier NGNOULAYE.")

# ---------------------------------------------------------------- 2. Plan
s = new_slide("Plan de la présentation", notes="Cinq parties : contexte et problématique, état de l'art, méthodologie proposée, résultats expérimentaux, puis conclusion et perspectives.")
plan = [("Contexte & problématique", "Enjeux de la détection faciale mobile en classe"),
        ("État de l'art", "Modèles légers, mécanismes d'attention, limites"),
        ("Méthodologie", "Architecture FeatherFace ECA-CBAM, entraînement multi-phase"),
        ("Résultats", "WIDER FACE, contexte réel, ablation"),
        ("Conclusion & perspectives", "Contributions, limites, travaux futurs")]
for i, (t, d) in enumerate(plan):
    y = 1.6 + i * 1.02
    flow_box(s, 0.9, y, 0.8, 0.8, f"0{i + 1}", NAVY if i % 2 == 0 else ACCENT, size=22)
    textbox(s, 1.95, y + 0.02, 9, 0.45, t, 22, True, NAVY)
    textbox(s, 1.95, y + 0.45, 9, 0.4, d, 15, False, GREY)

# ---------------------------------------------------------------- 3. Contexte
s = new_slide("Contexte de l'étude", "Contexte", notes=(
    "La reconnaissance faciale est devenue incontournable : sécurité, biométrie, systèmes embarqués. "
    "Le smartphone permet d'automatiser la vérification de présence en classe. Mais deux contraintes s'opposent : "
    "les ressources limitées du téléphone et la difficulté des images réelles (petits visages, éclairage, occlusions). "
    "Les détecteurs lourds comme Faster R-CNN ou YOLO standard ne sont pas adaptés ; les détecteurs légers à une phase sont la voie pragmatique."))
card(s, 0.6, 1.55, 3.95, 4.95, "Le besoin", [
    "Vérification de présence automatisée en salle de classe",
    "Smartphone : outil accessible, faible coût, non intrusif",
    "Suivi fiable des présences en milieu éducatif"], 16)
card(s, 4.7, 1.55, 3.95, 4.95, "Contraintes matérielles", [
    "Puissance de calcul limitée",
    "Mémoire restreinte",
    "Consommation énergétique",
    "Détecteurs lourds (Faster R-CNN, YOLO standard) inadaptés"], 16)
card(s, 8.8, 1.55, 3.95, 4.95, "Conditions réelles", [
    "Petits visages capturés à 2–5 m",
    "Occlusions : mains, masques, cheveux",
    "Éclairage variable : fenêtres, néons",
    "Poses non frontales, groupes denses"], 16, head=ACCENT)

# ---------------------------------------------------------------- 4. Problématique
s = new_slide("Problématique et questions de recherche", "Contexte", notes=(
    "Comment détecter de manière fiable des petits visages, partiellement occultés, sur un smartphone, "
    "sans sacrifier la vitesse ni la compacité ? Les combinaisons d'attention canal (ECA-Net) et spatiale (CBAM SAM) "
    "sont prometteuses, mais trois questions restent ouvertes."))
rect(s, 0.6, 1.55, 12.15, 1.45, NAVY)
textbox(s, 0.9, 1.6, 11.6, 1.35,
        "Comment concevoir un détecteur facial à la fois compact, rapide et précis sur les petits visages, "
        "déployable sur smartphone pour la vérification de présence en classe ?",
        21, True, WHITE, anchor=MSO_ANCHOR.MIDDLE)
qs = [("Q1", "Quel est le meilleur compromis compacité / précision des architectures hybrides pour les petits visages sur mobile ?"),
      ("Q2", "Comment stabiliser l'apprentissage multi-phase des modules d'attention, sans dominance d'un mécanisme sur l'autre ?"),
      ("Q3", "Une approche FeatherFace + attention ECA-CBAM répond-elle efficacement à la vérification de présence en milieu éducatif ?")]
for i, (q, t) in enumerate(qs):
    y = 3.3 + i * 1.15
    flow_box(s, 0.6, y, 0.9, 0.9, q, ACCENT, size=20)
    textbox(s, 1.7, y, 11, 0.9, t, 18, False, TEXT, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 5. Objectifs
s = new_slide("Objectifs de recherche", "Contexte", notes=(
    "Objectif principal : concevoir, implémenter et évaluer un modèle léger de détection faciale sur smartphone "
    "optimisé par une attention hybride ECA-Net + CBAM SAM. Il se décline en cinq objectifs spécifiques."))
textbox(s, 0.6, 1.45, 12.1, 0.8,
        "Objectif principal : concevoir, implémenter et évaluer un détecteur facial léger pour smartphone, "
        "optimisé par une attention hybride ECA-Net + CBAM SAM.", 18, True, NAVY)
objs = [("Étudier", "les détecteurs légers (SSD) et les modules d'attention ECA-Net et CBAM"),
        ("Intégrer", "l'attention hybride ECA-CBAM dans FeatherFace"),
        ("Développer", "une stratégie d'entraînement multi-phase stable"),
        ("Évaluer", "sur WIDER FACE et en salle de classe (précision, latence, taille)"),
        ("Comparer", "avec l'état de l'art et identifier les limites")]
for i, (v, t) in enumerate(objs):
    x = 0.6 + i * 2.47
    rect(s, x, 2.6, 2.3, 3.9, LIGHT)
    flow_box(s, x + 0.75, 2.85, 0.8, 0.8, str(i + 1), NAVY if i % 2 == 0 else ACCENT, size=22)
    textbox(s, x + 0.1, 3.85, 2.1, 0.5, v, 19, True, NAVY, PP_ALIGN.CENTER)
    textbox(s, x + 0.15, 4.4, 2.0, 2.0, t, 15, False, TEXT, PP_ALIGN.CENTER)

# ---------------------------------------------------------------- 6. État de l'art
s = new_slide("Modèles légers de détection faciale mobile", "État de l'art", notes=(
    "Du Viola-Jones aux réseaux profonds : les détecteurs à deux phases sont précis mais trop lourds ; "
    "les détecteurs à une phase sont privilégiés pour l'embarqué. BlazeFace est ultra-rapide mais faible sur les cas difficiles ; "
    "RetinaFace est précis mais dépasse 23M paramètres. FeatherFace CBAM est le meilleur compromis actuel : "
    "0,49M paramètres, environ 4 ms, 78,3 % de mAP hard."))
table(s, 0.6, 1.55, 7.6, [
    ["Modèle", "Backbone", "Attention", "Params", "mAP Hard", "Vitesse"],
    ["BlazeFace", "BlazeBlock", "Aucune", "0.3M", "~65 %", "~1 ms"],
    ["MobileFaceNets", "MobileNetV1", "Aucune", "1.0M", "~70 %", "~5 ms"],
    ["YOLOv5-nano", "CSPDarkNano", "Aucune", "1.9M", "~75 %", "5–7 ms"],
    ["RetinaFace", "ResNet50", "Aucune", ">23M", "~80 %", ">60 ms"],
    ["FeatherFace CBAM", "MobileNet-0.25", "CBAM", "0.49M", "78.3 %", "~4 ms"],
], col_w=[1.85, 1.6, 1.05, 0.95, 1.1, 1.05], size=14, highlight_last=True, row_h=0.6)
textbox(s, 0.6, 5.35, 7.6, 0.5, "Source : tableau comparatif du chapitre « Revue de la littérature ».", 12, False, GREY, italic=True)
card(s, 8.5, 1.55, 4.25, 4.95, "À retenir", [
    "Les détecteurs à une phase (SSD) sont la voie adaptée au mobile",
    "Sans attention : rapides, mais faibles sur le niveau hard",
    ("FeatherFace CBAM", " : meilleur compromis existant, référence de départ")], 16, head=ACCENT)

# ---------------------------------------------------------------- 7. Limites & positionnement
s = new_slide("Mécanismes d'attention : limites et positionnement", "État de l'art", notes=(
    "CBAM combine une attention canal (quoi) et spatiale (où). Mais sa partie canal utilise des couches entièrement connectées "
    "avec réduction de dimension : complexité O(C²). ECA-Net remplace cela par une convolution 1D adaptative, en O(C). "
    "D'où notre positionnement : garder l'attention spatiale de CBAM et remplacer son attention canal par ECA-Net, "
    "avec un entraînement multi-phase."))
card(s, 0.6, 1.55, 3.95, 3.6, "CBAM", [
    "Attention canal → « quoi »",
    "Attention spatiale → « où »",
    "Canal via couches FC : coût O(C²)"], 16)
card(s, 4.7, 1.55, 3.95, 3.6, "ECA-Net", [
    "Convolution 1D adaptative",
    "Pas de réduction de dimension",
    "Coût O(C), très peu de paramètres"], 16)
card(s, 8.8, 1.55, 3.95, 3.6, "Limites actuelles", [
    "Surcharge de l'attention canal",
    "Visages < 10 px difficiles",
    "Déséquilibre entre attentions à l'entraînement"], 16, head=ACCENT)
rect(s, 0.6, 5.4, 12.15, 1.25, NAVY)
textbox(s, 0.9, 5.45, 11.6, 1.15,
        "Positionnement : remplacer l'attention canal de CBAM par ECA-Net, conserver l'attention spatiale (SAM), "
        "et stabiliser l'ensemble par un entraînement multi-phase.", 19, True, WHITE, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 8. Architecture
s = new_slide("Architecture proposée : FeatherFace ECA-CBAM", "Méthodologie", notes=(
    "L'image d'entrée, redimensionnée en 640×640, passe dans le backbone MobileNet-0.25 qui extrait trois échelles : 64, 128 et 256 canaux. "
    "Trois modules ECA-CBAM raffinent ces sorties. Le BiFPN fusionne les échelles de façon bidirectionnelle (52 canaux), "
    "suivi de trois autres modules ECA-CBAM. Viennent ensuite le bloc SSH, le Channel Shuffle, et les têtes de détection : "
    "classification visage/fond, boîtes englobantes et 5 points de repère."))
steps = [("Entrée", "RGB 640×640", GREY), ("MobileNet-0.25", "64 / 128 / 256 canaux", NAVY),
         ("ECA-CBAM ×3", "niveau backbone", ACCENT), ("BiFPN", "fusion multi-échelle\n3 × 52 canaux", NAVY),
         ("ECA-CBAM ×3", "niveau BiFPN", ACCENT), ("SSH + Shuffle", "contexte multi-résolution", NAVY)]
bw, gap, y0 = 1.75, 0.33, 2.0
for i, (t, d, c) in enumerate(steps):
    x = 0.6 + i * (bw + gap)
    flow_box(s, x, y0, bw, 1.45, f"{t}\n{d}", c, size=15)
    if i < len(steps) - 1:
        arrow(s, x + bw + 0.03, y0 + 0.72, x + bw + gap - 0.03, y0 + 0.72)
arrow(s, 0.6 + 5 * (bw + gap) + bw / 2, y0 + 1.48, 0.6 + 5 * (bw + gap) + bw / 2, 4.05)
heads = [("Classification", "visage / fond"), ("Boîtes", "x, y, w, h"), ("Landmarks", "5 points faciaux")]
for i, (t, d) in enumerate(heads):
    flow_box(s, 6.95 + i * 1.95, 4.1, 1.8, 1.0, f"{t}\n{d}", WHITE, NAVY, 15).line.color.rgb = NAVY
textbox(s, 6.95, 5.2, 5.8, 0.4, "Têtes de détection multitâches", 14, True, NAVY, PP_ALIGN.CENTER)
card(s, 0.6, 4.05, 5.9, 2.6, "Idée clé", [
    "Attention hybride insérée à deux niveaux : backbone et BiFPN",
    "Complexité canal réduite de O(C²) à O(C)",
    "Base : FeatherFace CBAM (≈ 488 664 paramètres)"], 15, head=ACCENT)

# ---------------------------------------------------------------- 9. Module ECA-CBAM
s = new_slide("Le module hybride ECA-CBAM", "Méthodologie", notes=(
    "Le module enchaîne deux étapes. Étape 1, attention canal ECA : pooling global moyen, convolution 1D de taille k adaptative "
    "(gamma = 2, b = 1), sigmoïde, puis recalibrage des canaux. Étape 2, attention spatiale CBAM : max et moyenne le long des canaux, "
    "concaténation, convolution 7×7, sigmoïde, recalibrage spatial. Complexité totale O(C + H×W) contre O(C² + H×W) pour CBAM."))
flow_box(s, 0.6, 2.2, 1.6, 1.3, "Entrée F\nC × H × W", GREY, size=16)
arrow(s, 2.25, 2.85, 2.75, 2.85)
rect(s, 2.8, 1.55, 4.6, 2.6, LIGHT, line=NAVY)
textbox(s, 2.95, 1.62, 4.3, 0.45, "Étape 1 — Attention canal ECA", 17, True, NAVY)
bullets(s, 2.95, 2.1, 4.35, 2.0, ["GAP → descripteur z ∈ ℝᶜ",
                                  "Conv1D, noyau k adaptatif (γ = 2, b = 1)",
                                  "F_ECA = σ(Conv1D(z)) ⊙ F"], 15, gap=4)
arrow(s, 7.45, 2.85, 7.95, 2.85)
rect(s, 8.0, 1.55, 4.75, 2.6, LIGHT, line=ACCENT)
textbox(s, 8.15, 1.62, 4.5, 0.45, "Étape 2 — Attention spatiale CBAM", 17, True, ACCENT)
bullets(s, 8.15, 2.1, 4.5, 2.0, ["MaxPool + AvgPool sur les canaux",
                                 "Conv 7×7 → carte Mₛ = σ(·)",
                                 "F_out = Mₛ ⊙ F_ECA"], 15, gap=4)
metric(s, 0.6, 4.6, 3.8, "O(C + H×W)", "Complexité du module ECA-CBAM", ACCENT)
metric(s, 4.6, 4.6, 3.8, "O(C² + H×W)", "Complexité du CBAM classique", GREY)
card(s, 8.6, 4.45, 4.15, 2.2, "Pourquoi ce choix ?", [
    "ECA : ~95 % du gain de l'attention canal, coût ÷10",
    "SAM : référence pour la localisation"], 14)

# ---------------------------------------------------------------- 10. Entraînement multi-phase
s = new_slide("Stratégie d'entraînement multi-phase", "Méthodologie", notes=(
    "Phase 1 : attentions désactivées, le backbone, le BiFPN et les têtes s'adaptent seuls, Adam à 1e-3, batch 32. "
    "Phase 2a : on dégèle ECA, learning rate 5e-4 avec cosine annealing. Phase 2b : on dégèle CBAM SAM. "
    "Phase 3 : fine-tuning global à 1e-4, augmentation intensive, early stopping sur le mAP hard. "
    "La perte combine classification, boîtes et landmarks avec des poids 2, 1 et 0,5."))
phases = [("Phase 1", "Pré-entraînement", "Attentions à l'identité\nlr = 1e-3 · ≈ 30 epochs", GREY),
          ("Phase 2a", "Activation ECA", "Dégel ECA, SAM figé\nlr = 5e-4 · cosine", NAVY),
          ("Phase 2b", "Activation SAM", "Dégel CBAM SAM\nlr = 5e-4", NAVY),
          ("Phase 3", "Fine-tuning global", "Tout le réseau\nlr = 1e-4 · early stopping", ACCENT)]
for i, (p_, t, d, c) in enumerate(phases):
    x = 0.6 + i * 3.08
    flow_box(s, x, 1.6, 2.85, 0.75, f"{p_} — {t}", c, size=16)
    rect(s, x, 2.4, 2.85, 1.45, LIGHT)
    textbox(s, x + 0.1, 2.5, 2.65, 1.3, d, 15, False, TEXT, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    if i < 3:
        arrow(s, x + 2.88, 1.97, x + 3.06, 1.97)
card(s, 0.6, 4.15, 6.0, 2.5, "Perte multitâche", [
    "L = 2.0·L_cls + 1.0·L_bbox + 0.5·L_landmark",
    "Cross-entropy · Smooth L1 · Wing Loss"], 15)
card(s, 6.75, 4.15, 6.0, 2.5, "Régularisation", [
    "Adam, batch 32, 80–120 epochs au total",
    "Dropout 0.3 · weight decay 1e-4 · clipping 5.0",
    "Flip, color jitter, random crop, mixup (α = 0.2)"], 15, head=ACCENT)

# ---------------------------------------------------------------- 11. Protocole
s = new_slide("Protocole d'évaluation", "Méthodologie", notes=(
    "Évaluation principale sur WIDER FACE : 32 203 images, 393 703 visages, trois niveaux de difficulté. "
    "Le niveau hard regroupe les visages de moins de 10 pixels et les fortes occlusions : c'est le plus critique pour la classe. "
    "On mesure le mAP, la latence, le nombre de paramètres et la taille du modèle. "
    "Comparaison avec FeatherFace CBAM, BlazeFace, MobileFaceNets et YOLOv5-nano, plus une étude d'ablation et un test terrain."))
metric(s, 0.6, 1.55, 2.9, "32 203", "images WIDER FACE")
metric(s, 3.7, 1.55, 2.9, "393 703", "visages annotés")
metric(s, 6.8, 1.55, 2.9, "3", "niveaux : easy · medium · hard")
metric(s, 9.9, 1.55, 2.85, "500", "images terrain en classe")
card(s, 0.6, 3.2, 3.95, 3.45, "Métriques", [
    "mAP par niveau de difficulté",
    "Precision, Recall, F1",
    "Latence (ms / image)",
    "Paramètres et taille (MB)"], 15)
card(s, 4.7, 3.2, 3.95, 3.45, "Comparaisons", [
    "FeatherFace CBAM (baseline)",
    "BlazeFace · MobileFaceNets",
    "YOLOv5-nano · RetinaFace"], 15)
card(s, 8.8, 3.2, 3.95, 3.45, "Ablation", [
    "Sans attention",
    "CBAM seul · ECA seul",
    "ECA-CBAM (proposition)"], 15, head=ACCENT)

# ---------------------------------------------------------------- 12. Résultats WIDER FACE
s = new_slide("Résultats sur WIDER FACE", "Résultats", notes=(
    "FeatherFace ECA-CBAM atteint 92,5 % en easy, 90,8 % en medium et 80,0 % en hard, soit +1,7 point sur le hard "
    "par rapport à FeatherFace CBAM et +10 points par rapport à MobileFaceNets. La latence baisse de 20 %, de 4,0 à 3,2 ms "
    "sur GPU A100, et le modèle ne pèse que 1,4 MB."))
bar_chart(s, 0.6, 1.4, 7.7, 5.3, ["BlazeFace", "MobileFaceNets", "YOLOv5-nano", "FeatherFace CBAM", "ECA-CBAM"],
          [("mAP Hard (%)", (65.0, 70.0, 75.0, 78.3, 80.0))], "mAP Hard sur WIDER FACE (%)", vmin=50, vmax=85,
          point_colors={4: ACCENT})
metric(s, 8.6, 1.55, 2.0, "80.0 %", "mAP hard (+1.7 pt)")
metric(s, 10.75, 1.55, 2.0, "3.2 ms", "latence A100 (−20 %)")
metric(s, 8.6, 3.05, 2.0, "1.4 MB", "taille du modèle")
metric(s, 10.75, 3.05, 2.0, "92.5 %", "mAP easy (90.8 % medium)")
card(s, 8.6, 4.6, 4.15, 2.05, "Lecture", [
    "Gains sur les trois niveaux",
    "Meilleur compromis précision / vitesse / taille"], 14, head=ACCENT)

# ---------------------------------------------------------------- 13. Convergence
s = new_slide("Convergence de l'entraînement multi-phase", "Résultats", notes=(
    "Le mAP hard progresse à chaque phase : 72 % en fin de phase 1, 76,5 % après activation d'ECA, 78,8 % après SAM, "
    "et 80,0 % après le fine-tuning global. La perte passe de 8,5 à 2,1 en phase 1. "
    "Aucun surapprentissage : les courbes de validation et d'entraînement restent parallèles."))
bar_chart(s, 0.6, 1.4, 7.7, 5.3, ["Fin phase 1\n(ep. 30)", "Fin phase 2a\n(ep. 50)", "Fin phase 2b\n(ep. 70)", "Fin phase 3\n(ep. 100)"],
          [("mAP Hard (%)", (72.0, 76.5, 78.8, 80.0))], "Évolution du mAP Hard par phase (%)", vmin=65, vmax=82,
          chart_type=XL_CHART_TYPE.LINE_MARKERS, colors=[ACCENT])
card(s, 8.6, 1.55, 4.15, 5.1, "Observations", [
    ("+4.5 pt", " avec l'activation d'ECA"),
    ("+2.3 pt", " avec CBAM SAM"),
    ("+1.2 pt", " au fine-tuning global"),
    "Perte phase 1 : 8.5 → 2.1",
    "Pas de surapprentissage observé"], 16)

# ---------------------------------------------------------------- 14. Terrain
s = new_slide("Validation en salle de classe", "Résultats", notes=(
    "Test terrain sur 500 images capturées en classe avec un Samsung Galaxy S21, à 2–5 mètres, sous éclairage variable, "
    "avec 15 à 30 étudiants par image. Le modèle détecte 98 % des visages avec 1,8 % de faux positifs et une latence médiane "
    "de 10 ms sur Snapdragon 888. Qualitativement : bonne robustesse aux occlusions partielles et aux groupes denses."))
table(s, 0.6, 1.55, 7.7, [
    ["Modèle", "Recall", "Taux FP", "Latence smartphone"],
    ["BlazeFace", "89.0 %", "5.2 %", "8 ms"],
    ["MobileFaceNets", "92.5 %", "3.8 %", "15 ms"],
    ["FeatherFace CBAM", "96.0 %", "2.5 %", "12 ms"],
    ["FeatherFace ECA-CBAM", "98.0 %", "1.8 %", "10 ms"],
], col_w=[2.8, 1.5, 1.5, 1.9], size=15, highlight_last=True, row_h=0.62)
card(s, 0.6, 4.95, 7.7, 1.7, "Conditions du test", [
    "500 images · Galaxy S21 · 2–5 m · 15–30 personnes par image · néons, fenêtres, faible lumière"], 14)
metric(s, 8.6, 1.55, 4.15, "98 %", "des visages détectés (Recall)")
metric(s, 8.6, 3.05, 4.15, "< 2 %", "de faux positifs")
card(s, 8.6, 4.6, 4.15, 2.05, "Analyse qualitative", [
    "Occlusions partielles : 95 % de succès",
    "Visages de 8–12 px détectés"], 14, head=ACCENT)

# ---------------------------------------------------------------- 15. Ablation
s = new_slide("Étude d'ablation des mécanismes d'attention", "Résultats", notes=(
    "Quatre variantes entraînées dans les mêmes conditions. Sans attention : 72,5 %. CBAM complet : +5,8 points mais 4,0 ms. "
    "ECA seul : +4,3 points à 3,0 ms. L'hybride ECA-CBAM obtient le meilleur score, 80,0 %, avec 3,2 ms et 0,45M paramètres : "
    "les attentions canal et spatiale sont complémentaires."))
bar_chart(s, 0.6, 1.4, 6.6, 5.3, ["Sans attention", "CBAM complet", "ECA seul", "ECA-CBAM"],
          [("mAP Hard (%)", (72.5, 78.3, 76.8, 80.0))], "mAP Hard par variante (%)", vmin=60, vmax=85,
          point_colors={3: ACCENT})
table(s, 7.45, 1.55, 5.3, [
    ["Variante", "mAP Hard", "Latence", "Params"],
    ["Sans attention", "72.5 %", "2.8 ms", "0.42M"],
    ["+ CBAM complet", "78.3 %", "4.0 ms", "0.49M"],
    ["+ ECA seul", "76.8 %", "3.0 ms", "0.44M"],
    ["+ ECA-CBAM", "80.0 %", "3.2 ms", "0.45M"],
], col_w=[1.85, 1.15, 1.15, 1.15], size=14, highlight_last=True, row_h=0.55)
card(s, 7.45, 4.6, 5.3, 2.05, "Conclusion de l'ablation", [
    "+7.5 pt vs. sans attention, pour +0.4 ms",
    "Complémentarité canal (ECA) / spatial (SAM)"], 14, head=ACCENT)

# ---------------------------------------------------------------- 16. Discussion & limites
s = new_slide("Discussion et limites", "Résultats", notes=(
    "Face à RetinaFace, le modèle atteint 98 % de sa précision en étant 71 fois plus compact et 19 fois plus rapide. "
    "Limites : masques couvrant plus de 70 % du visage (68 % de détection), visages de moins de 5 pixels (45 %), contre-jour (15 % d'échecs), "
    "dépendance au jeu WIDER FACE, latence de 15–20 ms sur processeurs anciens, et fusion des attentions encore non pondérée."))
table(s, 0.6, 1.55, 6.0, [
    ["Modèle", "mAP Hard", "Latence", "Taille"],
    ["RetinaFace (ResNet50)", "81.5 %", "> 60 ms", "> 100 MB"],
    ["YOLOv5s", "79.0 %", "15–20 ms", "14 MB"],
    ["FeatherFace ECA-CBAM", "80.0 %", "3.2 ms", "1.4 MB"],
], col_w=[2.4, 1.2, 1.2, 1.2], size=14, highlight_last=True, row_h=0.55)
metric(s, 0.6, 4.0, 2.9, "71×", "plus compact que RetinaFace")
metric(s, 3.7, 4.0, 2.9, "19×", "plus rapide que RetinaFace")
textbox(s, 0.6, 5.5, 6.0, 1.1, "≈ 98 % de la précision de RetinaFace pour une fraction de son coût.", 16, True, NAVY)
card(s, 6.85, 1.55, 5.9, 5.1, "Limites identifiées", [
    ("Cas extrêmes", " : masques > 70 % (68 %), visages < 5 px (45 %), contre-jour"),
    ("Dataset", " : éclairage et poses de classe sous-représentés dans WIDER FACE"),
    ("Matériel ancien", " : 15–20 ms sur Snapdragon 660"),
    ("Fusion", " : coefficients α, β non encore appris")], 15, head=ACCENT)

# ---------------------------------------------------------------- 17. Conclusion & perspectives
s = new_slide("Contributions et perspectives", "Conclusion", notes=(
    "Trois contributions : l'architecture hybride ECA-CBAM pour la détection faciale mobile, la méthodologie d'entraînement multi-phase, "
    "et la validation applicative en classe. Perspectives : à court terme, données de classe annotées, quantification INT8 et coefficients adaptatifs ; "
    "à moyen terme, MAFA/FDDB, attention temporelle et multi-tâche ; à long terme, Vision Transformers légers, auto-supervision et microcontrôleurs."))
contribs = [("Architecture", "Hybride ECA-CBAM : 80.0 % mAP hard, 3.2 ms, 1.4 MB"),
            ("Méthodologie", "Entraînement multi-phase stable et généralisable"),
            ("Application", "98 % de Recall en salle de classe")]
for i, (t, d) in enumerate(contribs):
    y = 1.55 + i * 1.12
    flow_box(s, 0.6, y, 0.85, 0.85, str(i + 1), NAVY, size=22)
    textbox(s, 1.6, y - 0.02, 4.9, 0.45, t, 19, True, NAVY)
    textbox(s, 1.6, y + 0.4, 4.9, 0.6, d, 15, False, TEXT)
textbox(s, 6.85, 1.45, 5.9, 0.5, "Perspectives", 22, True, ACCENT)
terms = [("Court terme", "6–12 mois", ["Données de classe annotées", "INT8, pruning, ONNX", "Coefficients α, β appris"]),
         ("Moyen terme", "1–2 ans", ["FDDB, AFW, MAFA", "Attention temporelle (vidéo)", "Détection multi-tâche"]),
         ("Long terme", "2–5 ans", ["ViT légers (MobileViT)", "Auto-supervision", "Edge / IoT (STM32, ESP32)"])]
for i, (t, d, items) in enumerate(terms):
    x = 6.85 + i * 2.0
    rect(s, x, 2.05, 1.9, 4.6, LIGHT)
    rect(s, x, 2.05, 1.9, 0.08, ACCENT if i == 0 else NAVY)
    textbox(s, x + 0.08, 2.2, 1.75, 0.45, t, 17, True, NAVY, PP_ALIGN.CENTER)
    textbox(s, x + 0.08, 2.62, 1.75, 0.35, d, 13, False, GREY, PP_ALIGN.CENTER)
    bullets(s, x + 0.05, 3.15, 1.82, 3.4, items, 15, gap=10)
rect(s, 0.6, 5.0, 5.9, 1.65, NAVY)
textbox(s, 0.85, 5.05, 5.4, 1.55,
        "L'hybridation ECA-CBAM améliore à la fois la précision et l'efficacité de la détection faciale mobile.",
        17, True, WHITE, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 18. Merci
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, 13.333, 7.5, NAVY)
rect(s, 5.67, 4.1, 2.0, 0.06, ACCENT)
textbox(s, 0.6, 2.3, 12.1, 1.2, "Merci pour votre attention", 44, True, WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
textbox(s, 0.6, 3.35, 12.1, 0.6, "Questions & échanges", 24, False, ACCENT, PP_ALIGN.CENTER)
textbox(s, 0.6, 4.5, 12.1, 0.5, "FOKOU Arnaud Cedric  –  13Y180", 18, True, WHITE, PP_ALIGN.CENTER)
textbox(s, 0.6, 4.95, 12.1, 0.5, "Dr. AMINOU Halidou  ·  Dr. Janvier NGNOULAYE  ·  Université de Yaoundé I", 15, False,
        RGBColor(0xC9, 0xD3, 0xE0), PP_ALIGN.CENTER)
s.notes_slide.notes_text_frame.text = "Je vous remercie pour votre attention et reste à votre disposition pour vos questions."

number_slides()
OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(OUT, len(prs.slides), "slides")
