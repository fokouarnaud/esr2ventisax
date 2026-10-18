"""Contenu du stage de démonstration. Tout est fictif : personnes, entreprise, chantier et chiffres.

Les valeurs suivent le rapport modèle de tex_export_src/ (immeuble R+10, réducteurs du RDC au R+4, tubes PPR),
afin que l'import local produise un rapport complet et cohérent.
"""

import datetime

D = datetime.date
DEBUT, FIN = D(2026, 6, 1), D(2026, 9, 19)  # 16 semaines, du lundi au samedi

IDENTIFIANT = "demo.apprenant"
MOT_DE_PASSE = "demo-local-2026"

STAGE = {
    "intitule": "Stage de démonstration : plomberie sanitaire",
    "slug": "stage-demo",
    "specialite": "Froid et climatisation",
    "theme": "Plomberie sanitaire",
    "sous_theme": "Distribution d'eau froide et d'eau chaude sanitaire dans un immeuble à étages",
    "apprenant_nom": "DEMO Apprenant",
    "titre_rapport": "Distribution d'eau froide et d'eau chaude sanitaire dans un immeuble R+10",
    "type_rapport": "Rapport de stage",
    "tuteur_pro": "M. EXEMPLE Paul",
    "tuteur_pro_poste": "Conducteur des travaux",
    "tuteur_acad": "Mme MODÈLE Jeanne",
    "tuteur_acad_poste": "Formatrice en froid et climatisation",
    "entreprise": "Entreprise de démonstration",
    "entreprise_sigle": "EDEMO",
    "cfp": "Centre de formation professionnelle de démonstration",
    "cfp_sigle": "CFP-DÉMO",
    "diplome": "Diplôme de qualification professionnelle (DQP)",
    "annee_etude": "2e année",
    "session": "2026",
    "date_debut": DEBUT,
    "date_fin": FIN,
}

FICHE = {
    "presentation": "EDEMO est une SARL de droit camerounais spécialisée dans les **lots techniques du bâtiment** : "
                    "climatisation, plomberie sanitaire, électricité et détection incendie.",
    "organisation": "Une direction générale, une direction technique et cinq divisions (climatisation, plomberie, "
                    "électricité, réseaux et gaines, génie civil). Chaque division a ses chefs d'équipe.",
    "historique": "- 2010 : création par trois techniciens, premiers contrats d'entretien de climatiseurs ;\n"
                  "- 2014 : ouverture de la division plomberie ;\n"
                  "- 2019 : premier marché d'hôtel de grande hauteur ;\n"
                  "- 2024 : effectif porté à 45 salariés et création du service maintenance.",
    "secteurs": "Travaux neufs (lots techniques) et maintenance des installations.",
    "marches": "Bâtiment neuf (résidences, hôtels, bureaux) et contrats de maintenance.",
    "clients_fournisseurs": "Clients : Société immobilière Démo, Hôtel Exemple (Bonanjo), Clinique Fictive (Akwa). "
                            "Fournisseurs : Quincaillerie Démo SARL, Sanitaire Exemple Distribution, Froid Fictif "
                            "Import.",
    "concurrence": "Grandes entreprises générales, sociétés spécialisées et artisans informels aux prix bas.",
    "chiffres_cles": "Chiffre d'affaires 2025 : 450 millions de F CFA. Zone d'intervention : Douala, Yaoundé, Kribi.",
    "perspectives": "Atouts : offre multi-lots, expérience des grands chantiers. Faiblesses : dépendance aux "
                    "délais des fournisseurs. Opportunités : essor des hôtels. Menaces : concurrence informelle.",
    "mutations_technologiques": "Tubes PPR et multicouche à la place de l'acier galvanisé, climatiseurs inverter, "
                                "fluides à faible potentiel de réchauffement global.",
    "volonte_dirigeants": "Ouvrir une agence à Yaoundé en 2027 et créer une astreinte de maintenance 24 h/24.",
    "ville": "Douala",
    "quartier": "Akwa, rue de la Démonstration, face au carrefour Exemple",
    "annee_creation": "2010",
    "dirigeant": "M. FICTIF Alain",
    "capital": "10 000 000 F CFA",
    "effectif": "45 salariés",
    "contact": "BP 0000 Douala, +237 600 00 00 00, contact@entreprise-demo.example",
}

MISSION = {
    "poste": "Stagiaire technicien au sein de l'équipe plomberie du chantier Résidence Démo.",
    "position_organigramme": "Rattaché au chef d'équipe plomberie, sous l'autorité du chef de division plomberie.",
    "faits_importants": "- reprise d'un assemblage mal soudé lors du premier essai ;\n"
                        "- pression statique de 4,3 bar en pied de colonne ;\n"
                        "- rupture d'approvisionnement en raccords de 40 mm (deux jours de retard).",
    "objectifs_enjeux": "Réaliser la distribution d'eau froide et d'eau chaude des étages dans les délais, "
                        "sans fuite à l'essai.",
    "methodes_moyens": "Travail étage par étage : traçage, supports, préparation, polyfusion, raccordement, essai.",
    "collaborateurs": "Chef d'équipe plomberie, techniciens plombiers, équipe climatisation, magasinier.",
    "responsabilites": "Préparation des tubes, assemblages par polyfusion, montage des réducteurs, autocontrôles.",
    "resultats": "Six niveaux distribués (RDC au R+5), cinq réducteurs de pression et manomètres montés, "
                 "environ 280 m de canalisations isolées.",
    "difficultes_solutions": "Soudure défectueuse : reprise et respect des temps de chauffe. Raccords manquants : "
                             "réorganisation de l'ordre des étages.",
}

BILAN = {
    "pourquoi_ce_stage": "Découvrir un grand chantier et consolider le travail des tubes, commun au froid et à la "
                         "plomberie.",
    "appreciation": "Oui : l'équipe nous a confié des tâches réelles dès la troisième semaine.",
    "attentes_atteintes": "Oui pour la mise en œuvre ; moins pour le dimensionnement, fait au bureau d'études.",
    "apprecie_comme_stagiaire": "Le chef d'équipe a souligné notre rigueur dans les autocontrôles.",
    "resultats_remarques": "Nos fiches d'autocontrôle ont été reprises comme modèle pour l'équipe.",
    "travail_equipe": "Bonne entente ; coordination quotidienne avec l'équipe climatisation dans les gaines.",
    "consequence_carriere": "Confirme notre projet de technicien en froid et climatisation, avec une compétence "
                            "complémentaire en plomberie.",
    "critiques": "- plans d'exécution parfois en retard sur le chantier ;\n"
                 "- manque de fiches de procédure écrites pour la polyfusion.",
    "suggestions": "- afficher dans chaque local technique une fiche de réglage des réducteurs ;\n"
                   "- planifier les commandes de raccords deux semaines à l'avance.",
}

LIEUX = [
    {"cle": "siege", "nom": "Siège EDEMO", "type": "siege", "latitude": 4.0496, "longitude": 9.6942,
     "reperes": "Face au carrefour Exemple, immeuble à façade bleue", "ville": "Douala", "quartier": "Akwa"},
    {"cle": "chantier", "nom": "Résidence Démo", "type": "chantier", "latitude": 4.0255, "longitude": 9.6941,
     "reperes": "Derrière la station-service fictive, portail vert", "ville": "Douala", "quartier": "Bonapriso",
     "niveaux": "R+10"},
    {"cle": "fournisseur", "nom": "Quincaillerie Démo SARL", "type": "fournisseur", "latitude": 4.0560,
     "longitude": 9.7060, "reperes": "Marché central, entrée sud", "ville": "Douala", "quartier": "Bonabéri"},
]

PERSONNES = [
    # (clé, nom, fonction, rôle, à remercier)
    ("dg", "M. FICTIF Alain", "Directeur général", "autre", True),
    ("dt", "M. EXEMPLE Bernard", "Directeur technique", "autre", True),
    ("ct", "M. EXEMPLE Paul", "Conducteur des travaux", "encadreur_pro", True),
    ("cdp", "M. MODÈLE Charles", "Chef de division plomberie", "collegue", True),
    ("cdc", "Mme TYPE Diane", "Chef de division climatisation", "collegue", False),
    ("cep", "M. ESSAI Éric", "Chef d'équipe plomberie", "collegue", True),
    ("mag", "M. STOCK Félix", "Magasinier", "collegue", False),
    ("acad", "Mme MODÈLE Jeanne", "Formatrice en froid et climatisation", "encadreur_acad", True),
]

ABREVIATIONS = [
    ("CFP", "Centre de formation professionnelle"), ("DTU", "Document technique unifié"),
    ("ECS", "Eau chaude sanitaire"), ("EF", "Eau froide"), ("EPI", "Équipement de protection individuelle"),
    ("HSE", "Hygiène, sécurité et environnement"), ("MINEFOP", "Ministère de l'Emploi et de la Formation "
                                                              "professionnelle"),
    ("PPR", "Polypropylène random"), ("RDC", "Rez-de-chaussée"),
]

# (clé, type, auteur, titre, année, éditeur, url)
REFERENCES = [
    ("dtu601", "norme", "AFNOR", "NF DTU 60.1 : plomberie sanitaire pour bâtiments", 2012,
     "Association française de normalisation", ""),
    ("dtu6011", "norme", "AFNOR", "NF DTU 60.11 : règles de calcul des installations de plomberie sanitaire", 2013,
     "Association française de normalisation", ""),
    ("caleffi", "notice", "Caleffi", "Hydraulique n° 7 : les réducteurs de pression", 2010, "Caleffi", ""),
    ("ffb", "web", "Fédération française du bâtiment", "Les essais d'étanchéité des installations de plomberie",
     2020, "FFB", "https://www.ffbatiment.fr/"),
    ("wavin", "notice", "Wavin", "Système PP-R : tubes et raccords soudés par thermofusion", 2021, "Wavin", ""),
    ("chef", "oral", "M. ESSAI Éric", "Consignes de réglage des réducteurs sur le chantier", 2026, "", ""),
]

# (grandeur, valeur, unité, nature, clé de la référence ou indice de la note, date)
DONNEES = [
    ("Pression statique relevée au RDC", "4.3", "bar", "releve", None, D(2026, 8, 17)),
    ("Pression après réducteur au R+2", "3.0", "bar", "releve", None, D(2026, 8, 24)),
    ("Pression d'essai d'étanchéité", "10", "bar", "reference", "ffb", D(2026, 7, 27)),
    ("Durée de l'essai d'étanchéité", "2", "h", "reference", "ffb", D(2026, 7, 27)),
    ("Pression de réglage maximale aux points de puisage", "3", "bar", "reference", "dtu601", D(2026, 8, 17)),
    ("Température de soudage des tubes PPR", "260", "°C", "reference", "wavin", D(2026, 6, 22)),
    ("Débit de base d'un lavabo", "0.20", "L/s", "reference", "dtu6011", D(2026, 6, 10)),
]

# Organigramme : (clé, poste, nom, clé du parent, stagiaire)
ORGANIGRAMME = [
    ("dg", "Directeur général", "M. FICTIF Alain", None, False),
    ("dt", "Directeur technique", "", "dg", False),
    ("ct", "Conducteur des travaux", "M. EXEMPLE Paul", "dg", False),
    ("adm", "Administration et magasin", "", "dg", False),
    ("clim", "Division climatisation", "", "dt", False),
    ("plomb", "Division plomberie", "", "dt", False),
    ("elec", "Division électricité", "", "dt", False),
    ("cec", "Chef d'équipe climatisation", "", "clim", False),
    ("cep", "Chef d'équipe plomberie", "", "plomb", False),
    ("mag", "Magasinier", "", "adm", False),
    ("stg", "Stagiaire", "DEMO Apprenant", "cep", True),
]

CHAPITRES = [
    ("generalites", "Généralités sur la plomberie sanitaire"),
    ("chantier", "Présentation du chantier"),
    ("dimensionnement", "Dimensionnement d'une colonne d'eau froide"),
    ("materiel", "Matériaux et matériels utilisés"),
    ("modes", "Mise en œuvre : modes opératoires"),
    ("hse", "Hygiène, sécurité et environnement"),
    ("froid", "Liens avec le froid et la climatisation"),
]

# (désignation, catégorie, caractéristiques, rôle, quantité, slug de photo)
EQUIPEMENTS = [
    ("Polyfuseur", "outillage", "800 W, matrices de 20 à 63 mm", "Souder les tubes et raccords PPR", "1",
     "polyfuseur"),
    ("Coupe-tube", "outillage", "Lame inox, jusqu'à 63 mm", "Couper les tubes d'équerre", "2", "coupe_tube"),
    ("Perforateur", "outillage", "SDS Plus, 800 W", "Percer pour les supports", "1", ""),
    ("Clés à molette et clés plates", "outillage", "Jeu de 8 à 32 mm", "Serrer les raccords filetés", "1 jeu", ""),
    ("Tubes PPR PN20", "materiel", "Diamètres 20 à 63 mm", "Distribution d'eau froide et d'eau chaude", "≈ 600 m", ""),
    ("Réducteur de pression", "materiel", "Laiton, réglable de 1 à 6 bar", "Limiter la pression aux étages", "5",
     "reducteur_pression"),
    ("Flexible inox", "materiel", "1/2 pouce, 40 cm", "Raccorder les appareils sanitaires", "60", "flexible"),
    ("Isolant élastomère", "materiel", "Cellules fermées, 9 mm", "Limiter les pertes et la condensation", "≈ 280 m",
     "isolation_pose"),
    ("Casque de chantier", "epi", "Norme EN 397", "Protéger la tête", "1", "epi_chantier"),
    ("Chaussures de sécurité", "epi", "S3, embout acier", "Protéger les pieds", "1 paire", ""),
    ("Harnais antichute", "epi", "Deux longes", "Travaux en hauteur dans les gaines", "1", ""),
    ("Manomètre", "mesure", "0 à 10 bar, cadran 63 mm", "Contrôler la pression", "5", "manometre"),
    ("Pompe d'épreuve manuelle", "mesure", "0 à 60 bar", "Essais d'étanchéité", "1", "essai_etancheite"),
]

# (slug, légende, destination, illustration, clé du chapitre)
PHOTOS = [
    ("facade_chantier", "Façade principale du bâtiment du chantier", "corps", "immeuble", "chantier"),
    ("manometre", "Manomètre de contrôle", "corps", "cadran", "materiel"),
    ("reducteur_pression", "Réducteur de pression à membrane", "corps", "vanne", "materiel"),
    ("flexible", "Flexible de raccordement en inox", "corps", "flexible", "materiel"),
    ("coupe_tube", "Coupe-tube pour tubes PPR", "corps", "outil", "materiel"),
    ("polyfuseur", "Polyfuseur et ses matrices", "corps", "polyfuseur", "materiel"),
    ("reducteur_montage", "Montage du réducteur et du manomètre", "corps", "vanne", "modes"),
    ("isolation_pose", "Pose de l'isolant sur une canalisation", "corps", "isolation", "modes"),
    ("condensats_split", "Évacuation des condensats d'un split", "corps", "split", "froid"),
    ("epi_chantier", "EPI portés sur le chantier", "annexe", "casque", "hse"),
    ("essai_etancheite", "Pompe d'épreuve en essai d'étanchéité", "annexe", "cadran", "modes"),
    ("bon_livraison", "Bon de livraison des raccords de 40 mm", "preuve", "document", "materiel"),
]

# Tâches du Gantt (semaine de début, semaine de fin exclue), comme figures/gantt.tex du modèle.
# Chaque tâche fournit le contenu des notes quotidiennes de sa période.
TACHES = [
    {"libelle": "Accueil et sécurité", "semaines": (0, 1), "chapitre": "hse", "rubriques": [
        "entreprise.presentation", "entreprise.organisation", "entreprise.historique", "mission.poste",
        "mission.position_organigramme"],
     "activites": ["Accueil par le conducteur des travaux et présentation de l'entreprise.",
                   "Visite du chantier Résidence Démo et consignes de sécurité.",
                   "Lecture des plans d'exécution de plomberie avec le chef d'équipe."],
     "objectifs": "Connaître l'entreprise, le chantier et les règles de sécurité.",
     "methodologie": "Visite commentée, lecture des plans, remise des EPI.",
     "theorie": "Lecture d'un schéma de principe de distribution d'eau.",
     "difficultes": "Volume d'informations important la première semaine.",
     "solutions": "Prise de notes systématique dans le carnet de stage."},
    {"libelle": "Préparation et traçage", "semaines": (1, 3), "chapitre": "chantier", "rubriques": [
        "mission.methodes_moyens", "entreprise.clients_fournisseurs"],
     "activites": ["Inventaire du matériel livré par le magasinier.", "Traçage des réseaux au cordeau aux étages.",
                   "Repérage des passages dans les gaines techniques."],
     "objectifs": "Préparer le matériel et tracer les réseaux avant la pose.",
     "methodologie": "Comparaison bon de livraison et quantitatif, traçage au niveau et au cordeau.",
     "theorie": "Pentes, distances entre supports et repérage des réseaux.",
     "difficultes": "Plans d'exécution en retard sur deux étages.",
     "solutions": "Validation du tracé sur place avec le conducteur des travaux."},
    {"libelle": "Canalisations étages hauts", "semaines": (3, 6), "chapitre": "modes", "rubriques": [
        "mission.responsabilites", "mission.faits_importants"],
     "activites": ["Pose des supports et colliers aux étages supérieurs.",
                   "Assemblage des tubes PPR par polyfusion.", "Raccordement des distributions d'étage."],
     "objectifs": "Poser l'eau froide et l'eau chaude des étages R+6 à R+10.",
     "methodologie": "Coupe d'équerre, chauffe à 260 °C, emboîtement sans rotation, refroidissement.",
     "theorie": "Paramètres de soudage des tubes PPR selon le fabricant.",
     "difficultes": "Un assemblage mal chauffé a fui au premier essai.",
     "solutions": "Reprise de l'assemblage et respect strict des temps de chauffe."},
    {"libelle": "Canalisations étages bas", "semaines": (6, 8), "chapitre": "dimensionnement", "rubriques": [
        "mission.objectifs_enjeux", "entreprise.secteurs"],
     "activites": ["Pose des canalisations aux étages inférieurs.", "Raccordement aux colonnes montantes.",
                   "Calcul du débit probable d'une colonne avec le chef d'équipe."],
     "objectifs": "Achever la distribution des étages RDC à R+5.",
     "methodologie": "Même procédé que les étages hauts, avec contrôle des diamètres.",
     "theorie": "Débits de base, coefficient de simultanéité et choix des diamètres.",
     "difficultes": "Rupture d'approvisionnement en raccords de 40 mm.",
     "solutions": "Réorganisation de l'ordre des étages en attendant la livraison."},
    {"libelle": "Essais d'étanchéité", "semaines": (8, 9), "chapitre": "modes", "rubriques": [
        "mission.resultats"],
     "activites": ["Essai d'étanchéité par zone à 10 bar pendant 2 heures.", "Recherche et reprise d'une fuite.",
                   "Remplissage des fiches d'autocontrôle."],
     "objectifs": "Vérifier l'étanchéité des réseaux avant fermeture des gaines.",
     "methodologie": "Purge, mise en pression, isolement de la pompe, lecture du manomètre.",
     "theorie": "Pression et durée d'essai prescrites par le cahier des charges.",
     "difficultes": "Chute de pression lente sur une zone.",
     "solutions": "Contrôle des assemblages un par un et reprise du raccord fautif."},
    {"libelle": "Isolation des réseaux", "semaines": (9, 11), "chapitre": "froid", "rubriques": [
        "entreprise.mutations_technologiques"],
     "activites": ["Pose de l'isolant élastomère sur l'eau chaude.", "Collage des fentes et des jonctions.",
                   "Isolation des réseaux exposés en toiture."],
     "objectifs": "Limiter les pertes thermiques et la condensation.",
     "methodologie": "Découpe au cutter, collage néoprène, contrôle de la continuité.",
     "theorie": "Point de rosée et isolation à cellules fermées, comme en climatisation.",
     "difficultes": "Accès difficile dans les gaines étroites.",
     "solutions": "Pose de l'isolant avant la fixation définitive des tubes."},
    {"libelle": "Réducteurs et manomètres", "semaines": (11, 13), "chapitre": "dimensionnement", "rubriques": [
        "mission.collaborateurs"],
     "activites": ["Mesure de la pression statique au RDC : 4,3 bar.", "Montage des réducteurs entre deux vannes.",
                   "Réglage des réducteurs à 3 bar."],
     "objectifs": "Ramener la pression des étages RDC à R+4 sous 3 bar.",
     "methodologie": "Montage dans le sens de la flèche, manomètre en aval, réglage à débit nul.",
     "theorie": "Rapport de réduction et risque de cavitation.",
     "difficultes": "Pression variable selon l'heure de la journée.",
     "solutions": "Réglage contrôlé le matin et l'après-midi."},
    {"libelle": "Robinetterie et flexibles", "semaines": (13, 14), "chapitre": "materiel", "rubriques": [
        "entreprise.marches"],
     "activites": ["Pose des flexibles inox des lavabos.", "Montage de la robinetterie des salles d'eau.",
                   "Contrôle des serrages."],
     "objectifs": "Raccorder les appareils sanitaires.",
     "methodologie": "Serrage à la main puis quart de tour à la clé, joint fibre.",
     "theorie": "Rôle du flexible et du robinet d'arrêt.",
     "difficultes": "Flexibles de longueur insuffisante pour deux vasques.",
     "solutions": "Commande de flexibles de 50 cm."},
    {"libelle": "Appui climatisation", "semaines": (14, 15), "chapitre": "froid", "rubriques": [
        "entreprise.concurrence", "entreprise.chiffres_cles"],
     "activites": ["Pose de liaisons frigorifiques avec l'équipe climatisation.",
                   "Raccordement des évacuations de condensats.", "Échange sur le cycle frigorifique."],
     "objectifs": "Relier la plomberie à notre spécialité froid et climatisation.",
     "methodologie": "Cintrage, dudgeonnage, pente des condensats.",
     "theorie": "Cycle frigorifique et gestion des condensats.",
     "difficultes": "Coordination des passages dans les gaines.",
     "solutions": "Réunion de coordination quotidienne des deux équipes."},
    {"libelle": "Mise en eau et bilan", "semaines": (15, 16), "chapitre": "modes", "rubriques": [
        "mission.difficultes_solutions", "entreprise.perspectives", "entreprise.volonte_dirigeants"],
     "activites": ["Mise en eau des réseaux.", "Réglage final des pressions et autocontrôles.",
                   "Bilan du stage avec le tuteur professionnel."],
     "objectifs": "Livrer des réseaux en eau et faire le bilan du stage.",
     "methodologie": "Ouverture progressive des vannes, purge, relevés aux manomètres.",
     "theorie": "Contrôles de fonctionnement avant réception.",
     "difficultes": "Bulles d'air dans les étages hauts.",
     "solutions": "Purge par les points hauts."},
]

# Rédaction de démonstration : un \AC{…} des parties du modèle est reconnu par le début de « contenu}suite »
# et remplacé, accolades comprises, par la valeur (LaTeX brut).
REDACTION = {
    "Étapes clés de l'historique": "Fondée par trois techniciens autour de contrats d'entretien de "
        "climatiseurs, l'entreprise a ouvert sa division plomberie en 2014, obtenu son premier marché d'hôtel de "
        "grande hauteur en 2019 et créé son service maintenance en 2024.",
    "Nom} & Directeur technique": "M. EXEMPLE Bernard",
    "Nom} & Chef de division plomberie": "M. MODÈLE Charles",
    "Nom} & Chef de division climatisation": "Mme TYPE Diane",
    "Nom} & Chef d'équipe plomberie": "M. ESSAI Éric",
    "Nom} & Magasinier": "M. STOCK Félix",
    "Exemples de clients": "Parmi ses références figurent la Résidence Démo (Bonapriso), l'Hôtel Exemple (Bonanjo) "
        "et la Clinique Fictive (Akwa).",
    "Principaux fournisseurs": "Ses principaux fournisseurs sont Quincaillerie Démo SARL, Sanitaire Exemple "
        "Distribution et Froid Fictif Import.",
    "montant": "450 millions de F CFA (2025)",
    "villes, régions, pays": "Douala, Yaoundé, Kribi",
    "Projets annoncés": "La direction a annoncé l'ouverture d'une agence à Yaoundé en 2027 et la création d'une "
        "astreinte de maintenance 24~h/24.",
    "nombre} niveaux": "six (06)",
    "nombre} réducteurs": "cinq (05)",
    "longueur": "280",
    "Maître d'ouvrage": "Le maître d'ouvrage est la Société immobilière Démo et la maîtrise d'œuvre est assurée par "
        "le Cabinet Exemple Architectes. Le bâtiment compte 40 chambres d'hôtel et 16 logements ; à notre "
        "arrivée, le gros œuvre était achevé et les cloisons étaient en cours.",
    "pression d'essai": "\\SI{10}{bar} pendant \\SI{2}{h}, sans chute de pression",
}
