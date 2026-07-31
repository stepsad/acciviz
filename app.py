import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import locale

locale.setlocale(locale.LC_ALL, "fr-FR.UTF-8")

# =============================================================
# FONCTIONS
# =============================================================

@st.cache_data
def load_data(year=2024, dept='57 Moselle', id_grav=0):
    """Charger les 4 fichiers suivants : caractéristiques, lieux, véhicules, usagers. Puis les fusionner dans un unique jeu de donnée 'df_accident'.

    Args:
        year (int, optionel): l'année issue du filtre 'Année'. Par défaut 2024.
        dept (str, optionel): le département issu du filtre 'Département'. Par défaut '57 Moselle'.
        id_grav (int, optionel): l'identifiant BAAC de la gravité de blessure de l'usager. Par défaut = 0, c'est à dire toutes les gravité.

    Returns:
        Any: le jeu de données 'df_accident'.
    """
    df_caracteristique = pd.read_csv(f"data/caracteristiques-{year}.csv", sep=";")
    df_lieu = pd.read_csv(f"data/lieux-{year}.csv", sep=";", low_memory=False)
    df_vehicule = pd.read_csv(f"data/vehicules-{year}.csv", sep=";")
    df_usager = pd.read_csv(f"data/usagers-{year}.csv", sep=";")

    code_dept = dept.split(sep=" ")
    df_caracteristique = df_caracteristique[df_caracteristique["dep"] == code_dept[0]]

    if id_grav != 0:
        df_usager = df_usager[df_usager["grav"] == id_grav]

    df_lieu = df_lieu.sort_values(["Num_Acc", "catr"])
    df_lieu = df_lieu.drop_duplicates(subset="Num_Acc", keep="first")

    df_accident = pd.merge(df_caracteristique, df_lieu, how="left", on="Num_Acc")
    df_accident = pd.merge(df_accident, df_vehicule, how="left", on="Num_Acc")
    df_accident = pd.merge(df_accident, df_usager, how="left", on=["Num_Acc", "id_vehicule"])   

    return df_accident, df_caracteristique, df_lieu, df_vehicule, df_usager

def prepare_data(df_accident):
    """Préparer le jeu de données 'df_accident' pour la génération du tableau de bord.

    Args:
        df_accident (Any): jeu de données 'df_accident' avant préparation

    Returns:
        Any: le jeu de données 'df_accident' préparé.
    """
    # Caster les colonnes 'lat' et 'long' en entier
    df_accident['lat'] = df_accident['lat'].str.replace(',', '.')
    df_accident['long'] = df_accident['long'].str.replace(',', '.')
    df_accident[['lat', 'long']] = df_accident[['lat', 'long']].apply(pd.to_numeric)

    # Ajouter une colonne 'date'
    df_accident = df_accident.assign(date = 'NA')
    df_accident['datetime'] = df_accident['an'].map(str) + "-" + df_accident['mois'].map(str) + "-" + df_accident['jour'].map(str)
    df_accident['datetime'] = pd.to_datetime(df_accident['datetime'] + " " + df_accident['hrmn'])

    # Ajouter une colonne 'heure'
    df_accident['heure'] = df_accident['datetime'].dt.hour

    # Ajouter une colonne 'agg_2'
    df_accident = df_accident.assign(agg_2 = 'Hors agglomération')
    df_accident.loc[df_accident['agg'] == 2, 'agg_2'] = 'En agglomération'

    # Ajouter une colonne 'int_2'
    df_accident = df_accident.assign(int_2 = 'Hors intersection')
    df_accident.loc[df_accident.int == 2, 'int_2'] = 'En intersection'
    df_accident.loc[df_accident.int == 3, 'int_2'] = 'En intersection'
    df_accident.loc[df_accident.int == 4, 'int_2'] = 'En intersection'
    df_accident.loc[df_accident.int == 5, 'int_2'] = 'En intersection'
    df_accident.loc[df_accident.int == 6, 'int_2'] = 'En intersection'
    df_accident.loc[df_accident.int == 7, 'int_2'] = 'Autre'
    df_accident.loc[df_accident.int == 8, 'int_2'] = 'Autre'
    df_accident.loc[df_accident.int == 9, 'int_2'] = 'Autre'

    # Ajouter une colonne 'catr_2'
    df_accident = df_accident.assign(catr_2 = 'RD')
    df_accident.loc[df_accident.catr == 1, 'catr_2'] = 'A'
    df_accident.loc[df_accident.catr == 2, 'catr_2'] = 'RN'
    df_accident.loc[df_accident.catr == 4, 'catr_2'] = 'VC'
    df_accident.loc[df_accident.catr == 5, 'catr_2'] = 'Autre'
    df_accident.loc[df_accident.catr == 6, 'catr_2'] = 'Autre'
    df_accident.loc[df_accident.catr == 7, 'catr_2'] = 'RM'
    df_accident.loc[df_accident.catr == 9, 'catr_2'] = 'Autre'

    # Ajouter une colonne 'atm_2'
    df_accident = df_accident.assign(atm_2 = 'Normale')
    df_accident.loc[df_accident.atm == -1, 'atm_2'] = 'Non renseignée'
    df_accident.loc[df_accident.atm == 2, 'atm_2'] = 'Dégradée'
    df_accident.loc[df_accident.atm == 3, 'atm_2'] = 'Dégradée'
    df_accident.loc[df_accident.atm == 4, 'atm_2'] = 'Dégradée'
    df_accident.loc[df_accident.atm == 5, 'atm_2'] = 'Dégradée'
    df_accident.loc[df_accident.atm == 6, 'atm_2'] = 'Dégradée'
    df_accident.loc[df_accident.atm == 7, 'atm_2'] = 'Dégradée'
    df_accident.loc[df_accident.atm == 8, 'atm_2'] = 'Dégradée'
    df_accident.loc[df_accident.atm == 9, 'atm_2'] = 'Autre'

    # Ajouter une colonne 'surf_2'
    df_accident = df_accident.assign(surf_2 = 'Normale')
    df_accident.loc[df_accident.surf == -1, 'surf_2'] = 'Non renseigné'
    df_accident.loc[df_accident.surf == 2, 'surf_2'] = 'Dégradé'
    df_accident.loc[df_accident.surf == 3, 'surf_2'] = 'Dégradé'
    df_accident.loc[df_accident.surf == 4, 'surf_2'] = 'Dégradé'
    df_accident.loc[df_accident.surf == 5, 'surf_2'] = 'Dégradé'
    df_accident.loc[df_accident.surf == 6, 'surf_2'] = 'Dégradé'
    df_accident.loc[df_accident.surf == 7, 'surf_2'] = 'Dégradé'
    df_accident.loc[df_accident.surf == 8, 'surf_2'] = 'Dégradé'
    df_accident.loc[df_accident.surf == 9, 'surf_2'] = 'Autre'

    # Ajouter une colonne 'catv_2'
    df_accident = df_accident.assign(catv_2 = 'VT')
    df_accident.loc[df_accident["catv"].isin([0, 3, 20, 21, 35, 36, 37, 38, 39, 40, 99]), 'catv_2'] = 'Autres'
    df_accident.loc[df_accident["catv"] == 50, 'catv_2'] = 'EDP-m'
    df_accident.loc[df_accident["catv"].isin([1, 60, 80]), 'catv_2'] = 'Vélo'
    df_accident.loc[df_accident["catv"].isin([2, 30, 31, 32, 33, 34, 41, 42, 43]), 'catv_2'] = '2RM'
    df_accident.loc[df_accident["catv"] == 10, 'catv_2'] = 'VU'
    df_accident.loc[df_accident["catv"].isin([13, 14, 15, 16, 17]), 'catv_2'] = 'PL'

    # Ajouter une colonne 'grav_2'
    df_accident = df_accident.assign(grav_2 = 'Indemne')
    df_accident.loc[df_accident.grav == 2, 'grav_2'] = 'Tué'
    df_accident.loc[df_accident.grav == 3, 'grav_2'] = 'Blessé hospitalisé'
    df_accident.loc[df_accident.grav == 4, 'grav_2'] = 'Blessé léger'

    # Ajouter une colonne 'classe_age'
    df_accident = df_accident.assign(classe_age = '0-17')
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 17, 'classe_age'] = '18-24'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 24, 'classe_age'] = '25-34'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 34, 'classe_age'] = '35-44'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 44, 'classe_age'] = '45-54'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 54, 'classe_age'] = '55-64'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 64, 'classe_age'] = '65+'

    # Ajouter une colonne 'lum_2'
    df_accident = df_accident.assign(lum_2 = 'Jour')
    df_accident.loc[df_accident.lum == 3, 'lum_2'] = 'Nuit'
    df_accident.loc[df_accident.lum == 4, 'lum_2'] = 'Nuit'
    df_accident.loc[df_accident.lum == 5, 'lum_2'] = 'Nuit'

    return df_accident

def calculate_indicators(df):
    """_summary_

    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """
    df_grav_1 = (df.loc[df["grav"] == 1, ["Num_Acc", "grav"]]
                   .rename(columns={"grav":"I"})
                   .groupby(by="Num_Acc")
                   .count()
                   .reset_index()
                )
    df_grav_2 = (df.loc[df["grav"] == 2, ["Num_Acc", "grav"]]
                   .rename(columns={"grav":"T"})
                   .groupby(by="Num_Acc")
                   .count()
                   .reset_index()
                )
    df_grav_3 = (df.loc[df["grav"] == 3, ["Num_Acc", "grav"]]
                   .rename(columns={"grav":"BH"})
                   .groupby(by="Num_Acc")
                   .count()
                   .reset_index()
                )
    df_grav_4 = (df.loc[df["grav"] == 4, ["Num_Acc", "grav"]]
                   .rename(columns={"grav":"BL"})
                   .groupby(by="Num_Acc")
                   .count()
                   .reset_index()
                )

    df_grav = pd.merge(df_grav_1, df_grav_2, how="outer", on="Num_Acc")
    df_grav = pd.merge(df_grav, df_grav_3, how="outer", on="Num_Acc")
    df_grav = pd.merge(df_grav, df_grav_4, how="outer", on="Num_Acc")

    df_grav.reset_index()
    df_grav.fillna(0, inplace=True)

    df_grav = df_grav.assign(AM = lambda x : np.where(x["T"] >= 1, 1, 0))
    df_grav = df_grav.assign(AGNM = lambda x : np.where((x["T"] == 0) & (x.BH >= 1), 1, 0))
    df_grav = df_grav.assign(AL = lambda x : np.where((x["T"] == 0) & (x.BH == 0) & (x.BL >= 1), 1, 0))

    return df_grav

def list_dept():
    """_summary_

    Returns:
        _type_: _description_
    """
    # Métropole (01–95, + 2A, 2B pour la Corse)
    metro = [
        ('01', 'Ain', '01 Ain', 698810),
        ('02', 'Aisne', '02 Aisne', 515993),
        ('03', 'Allier', '03 Allier', 330281),
        ('04', 'Alpes-de-Haute-Provence', '04 Alpes-de-Haute-Provence', 170438),
        ('05', 'Hautes-Alpes', '05 Hautes-Alpes', 145889),
        ('06', 'Alpes-Maritimes', '06 Alpes-Maritimes', 1154619),
        ('07', 'Ardèche', '07 Ardèche', 338154),
        ('08', 'Ardennes', '08 Ardennes', 261420),
        ('09', 'Ariège', '09 Ariège', 157151),
        ('10', 'Aube', '10 Aube', 307946),
        ('11', 'Aude', '11 Aude', 381829),
        ('12', 'Aveyron', '12 Aveyron', 278384),
        ('13', 'Bouches-du-Rhône', '13 Bouches-du-Rhône', 2119367),
        ('14', 'Calvados', '14 Calvados', 718525),
        ('15', 'Cantal', '15 Cantal', 143807),
        ('16', 'Charente', '16 Charente', 352694),
        ('17', 'Charente-Maritime', '17 Charente-Maritime', 686414),
        ('18', 'Cher', '18 Cher', 295279),
        ('19', 'Corrèze', '19 Corrèze', 241707),
        ('21', 'Côte-d''Or', '21 Côte-d''Or', 542484),
        ('22', 'Côtes-d''Armor', '22 Côtes-d''Armor', 617550),
        ('23', 'Creuse', '23 Creuse', 114943),
        ('24', 'Dordogne', '24 Dordogne', 421332),
        ('25', 'Doubs', '25 Doubs', 546618),
        ('26', 'Drôme', '26 Drôme', 528418),
        ('27', 'Eure', '27 Eure', 603667),
        ('28', 'Eure-et-Loir', '28 Eure-et-Loir', 433197),
        ('29', 'Finistère', '29 Finistère', 945340),
        ('2A', 'Corse-du-Sud', '2A Corse-du-Sud', 175148),
        ('2B', 'Haute-Corse', '2B Haute-Corse', 190488),
        ('30', 'Gard', '30 Gard', 786657),
        ('31', 'Haute-Garonne', '31 Haute-Garonne', 1519613),
        ('32', 'Gers', '32 Gers', 192488),
        ('33', 'Gironde', '33 Gironde', 1735915),
        ('34', 'Hérault', '34 Hérault', 1264791),
        ('35', 'Ille-et-Vilaine', '35 Ille-et-Vilaine', 1148210),
        ('36', 'Indre', '36 Indre', 212712),
        ('37', 'Indre-et-Loire', '37 Indre-et-Loire', 624278),
        ('38', 'Isère', '38 Isère', 1316321),
        ('39', 'Jura', '39 Jura', 256448),
        ('40', 'Landes', '40 Landes', 446475),
        ('41', 'Loir-et-Cher', '41 Loir-et-Cher', 326899),
        ('42', 'Loire', '42 Loire', 777387),
        ('43', 'Haute-Loire', '43 Haute-Loire', 229372),
        ('44', 'Loire-Atlantique', '44 Loire-Atlantique', 1522543),
        ('45', 'Loiret', '45 Loiret', 696921),
        ('46', 'Lot', '46 Lot', 177544),
        ('47', 'Lot-et-Garonne', '47 Lot-et-Garonne', 335539),
        ('48', 'Lozère', '48 Lozère', 76442),
        ('49', 'Maine-et-Loire', '49 Maine-et-Loire', 843530),
        ('50', 'Manche', '50 Manche', 498153),
        ('51', 'Marne', '51 Marne', 556991),
        ('52', 'Haute-Marne', '52 Haute-Marne', 164723),
        ('53', 'Mayenne', '53 Mayenne', 303649),
        ('54', 'Meurthe-et-Moselle', '54 Meurthe-et-Moselle', 729051),
        ('55', 'Meuse', '55 Meuse', 177105),
        ('56', 'Morbihan', '56 Morbihan', 798958),
        ('57', 'Moselle', '57 Moselle', 1049746),
        ('58', 'Nièvre', '58 Nièvre', 199498),
        ('59', 'Nord', '59 Nord', 2613295),
        ('60', 'Oise', '60 Oise', 826785),
        ('61', 'Orne', '61 Orne', 271549),
        ('62', 'Pas-de-Calais', '62 Pas-de-Calais', 1448930),
        ('63', 'Puy-de-Dôme', '63 Puy-de-Dôme', 664282),
        ('64', 'Pyrénées-Atlantiques', '64 Pyrénées-Atlantiques', 723077),
        ('65', 'Hautes-Pyrénées', '65 Hautes-Pyrénées', 232323),
        ('66', 'Pyrénées-Orientales', '66 Pyrénées-Orientales', 509332),
        ('67', 'Bas-Rhin', '67 Bas-Rhin', 1174367),
        ('68', 'Haut-Rhin', '68 Haut-Rhin', 771128),
        ('69', 'Rhône', '69 Rhône', 1937017),
        ('70', 'Haute-Saône', '70 Haute-Saône', 231130),
        ('71', 'Saône-et-Loire', '71 Saône-et-Loire', 547965),
        ('72', 'Sarthe', '72 Sarthe', 565033),
        ('73', 'Savoie', '73 Savoie', 455152),
        ('74', 'Haute-Savoie', '74 Haute-Savoie', 884180),
        ('75', 'Paris', '75 Paris', 2047602),
        ('76', 'Seine-Maritime', '76 Seine-Maritime', 1261832),
        ('77', 'Seine-et-Marne', '77 Seine-et-Marne', 1502094),
        ('78', 'Yvelines', '78 Yvelines', 1514418),
        ('79', 'Deux-Sèvres', '79 Deux-Sèvres', 374788),
        ('80', 'Somme', '80 Somme', 560761),
        ('81', 'Tarn', '81 Tarn', 402529),
        ('82', 'Tarn-et-Garonne', '82 Tarn-et-Garonne', 267905),
        ('83', 'Var', '83 Var', 1148634),
        ('84', 'Vaucluse', '84 Vaucluse', 579423),
        ('85', 'Vendée', '85 Vendée', 730471),
        ('86', 'Vienne', '86 Vienne', 436529),
        ('87', 'Haute-Vienne', '87 Haute-Vienne', 372371),
        ('88', 'Vosges', '88 Vosges', 351794),
        ('89', 'Yonne', '89 Yonne', 329814),
        ('90', 'Territoire de Belfort', '90 Territoire de Belfort', 140086),
        ('91', 'Essonne', '91 Essonne', 1364840),
        ('92', 'Hauts-de-Seine', '92 Hauts-de-Seine', 1675904),
        ('93', 'Seine-Saint-Denis', '93 Seine-Saint-Denis', 1745657),
        ('94', 'Val-de-Marne', '94 Val-de-Marne', 1439001),
        ('95', 'Val-d''Oise', '95 Val-d''Oise', 1304986),
    ]

    # DOM-TOM (DROM + COM principaux)
    domtom = [
        ('971', 'Guadeloupe', '971 Guadeloupe', 382586),
        ('972', 'Martinique', '972 Martinique', 358818),
        ('973', 'Guyane', '973 Guyane', 298554),
        ('974', 'La Réunion', '974 La Réunion', 910985),
        ('976', 'Mayotte', '975 Mayotte', 338208),
        ('975', 'Saint-Pierre-et-Miquelon', '976 Saint-Pierre-et-Miquelon', None),
        ('977', 'Saint-Barthélemy', '977 Saint-Barthélemy', None),
        ('978', 'Saint-Martin', '978 Saint-Martin', None),
        ('986', 'Wallis-et-Futuna', '986 Wallis-et-Futuna', None),
        ('987', 'Polynésie française', '987 Polynésie française', None),
        ('988', 'Nouvelle-Calédonie', '988 Nouvelle-Calédonie', None),
    ]

    return metro + domtom    

def get_info_dept(nom_recherche):
    """Retourne le tuple (code, nom, pop) dont le nom correspond exactement.
    Retourne None si aucun département ne correspond.

    Args:
        nom_recherche (str): Le nom complet du département (code_insee + libellé)

    Returns:
        tuple: le tuple trouvé (code_insee, nom, nom_complet, pop)
    """
    for code, nom, nom_complet, pop in list_dept():
        if nom_complet == nom_recherche:
            return (code, nom, nom_complet, pop)
    return None

def get_id_grav(grav):
    if grav == "Tués":
        return 2

    if grav == "Blessés hospitalisés":
        return 3

    if grav == "Blessés légers":
        return 4

    return 0


def generate_graph(df_vic):
    COLOR = px.colors.sequential.Redor

    # agg-graph ----------------------------------
    df_vic = df_vic.assign(agg_2 = 'Hors agglomération')
    df_vic.loc[df_vic['agg'] == 2, 'agg_2'] = 'En agglomération'
    df_vicGroupBy = df_vic.groupby('agg_2').count()
    fig1 = px.pie(
        df_vicGroupBy, 
        values="Num_Acc", 
        names=df_vicGroupBy.index,
        labels={
            "Num_Acc": "Victimes",
            "agg_2": "Localisation"
        }, 
        title="Part des victimes par localisation",
        color_discrete_sequence=COLOR
    )
    fig1.update_traces(pull=0.01)

    # int-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('int_2').count()
    fig2 = px.pie(
        df_vicGroupBy, 
        values="Num_Acc", 
        names=df_vicGroupBy.index,
        labels={
            "Num_Acc": "Victimes",
            "int_2": "Intersection"
        }, 
        title="Part des victimes par intersection",
        color_discrete_sequence=COLOR
    )
    fig2.update_traces(pull=0.01)

    # lum-graph -----------------------------
    df_vicGroupBy = df_vic.groupby('lum_2').count()
    fig3 = px.pie(
        df_vicGroupBy, 
        values="Num_Acc", 
        names=df_vicGroupBy.index,
        labels={
            "Num_Acc": "Victimes",
            "lum_2": "Luminosité"
        }, 
        title="Part des victimes par luminosité",
        color_discrete_sequence=COLOR
    )
    fig3.update_traces(pull=0.01)

    # catr-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('catr_2').count()
    fig4 = px.bar(
        df_vicGroupBy,
        x=df_vicGroupBy.index,
        y='Num_Acc',
        labels={
            "Num_Acc": "Victimes",
            "catr_2": "Cat. route"
        },
        title="Victimes par catégorie de route",
        text='Num_Acc',
        color_discrete_sequence=COLOR
    )

    # atm-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('atm_2').count()
    fig5 = px.bar(
        df_vicGroupBy,
        x=df_vicGroupBy.index,
        y='Num_Acc',
        labels={
            "Num_Acc": "Victimes",
            "atm_2": "Cond. atmosphériques"
        },
        title="Victimes par conditions atmosphériques",
        text='Num_Acc',
        color_discrete_sequence=COLOR
    )

    # surf-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('surf_2').count()
    fig6 = px.bar(
        df_vicGroupBy,
        x=df_vicGroupBy.index,
        y='Num_Acc',
        labels={
            "Num_Acc": "Victimes",
            "surf_2": "Etat surface"
        },
        title="Victimes selon l'état de surface de la chaussée",
        text='Num_Acc',
        color_discrete_sequence=COLOR
    )

    # catu-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('catu').count()
    df_vicGroupBy.rename(index={1: 'Conducteur', 2: 'Passager', 3: 'Piéton'}, inplace=True)
    fig7 = px.pie(
        df_vicGroupBy, 
        values="Num_Acc", 
        names=df_vicGroupBy.index,
        labels={
            "Num_Acc": "Victimes",
            "catu": "Cat. usager"
        }, 
        title="Part des victimes par catégorie d'usager",
        color_discrete_sequence=COLOR
    )
    fig7.update_traces(pull=0.01)

    # sexe-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('sexe').count()
    df_vicGroupBy.rename(index={1: 'Masculin', 2: 'Féminin'}, inplace=True)
    fig8 = px.pie(
        df_vicGroupBy, 
        values="Num_Acc", 
        names=df_vicGroupBy.index,
        labels={
            "Num_Acc": "Victimes",
            "sexe": "Sexe"
        }, 
        title="Part des victimes par sexe",
        color_discrete_sequence=COLOR
    )
    fig8.update_traces(pull=0.01)

    # classe_age-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('classe_age').count()
    fig9 = px.bar(
        df_vicGroupBy,
        x=df_vicGroupBy.index,
        y='Num_Acc',
        labels={
            "Num_Acc": "Victimes",
            "classe_age": "Classe d'âge"
        },
        title="Victimes selon la classe d'âge",
        text='Num_Acc',
        color_discrete_sequence=COLOR
    )

    # trajet-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('trajet').count()
    df_vicGroupBy.rename(
        index={
            -1: 'Non renseigné',
            0: 'Non renseigné',
            1: 'Domicile - travail', 
            2: 'Domicile - école', 
            3: 'Courses - achats',
            4: 'Utilisation professionnel',
            5: 'Promenade - loisirs',
            9: 'Autre'
        }, 
        inplace=True
    )
    fig10 = px.bar(
        df_vicGroupBy,
        x=df_vicGroupBy.index,
        y='Num_Acc',
        labels={
            "Num_Acc": "Victimes",
            "trajet": "Trajet"
        },
        title="Victimes selon le type de trajet",
        text='Num_Acc',
        color_discrete_sequence=COLOR
    )

    # mois-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('mois').count()
    df_vicGroupBy.rename(
        index={
            1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Juin',
            7: 'Juil', 8: 'Aoû', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'
        }, 
        inplace=True
    )
    fig11 = px.bar(
        df_vicGroupBy,
        x=df_vicGroupBy.index,
        y='Num_Acc',
        labels={
            "Num_Acc": "Victimes",
            "mois": "Mois"
        },
        title="Victimes selon le mois",
        text='Num_Acc',
        color_discrete_sequence=COLOR
    )

    # catv-graph ----------------------------------
    df_vicGroupBy = df_vic.groupby('catv_2').count()
    fig12 = px.bar(
        df_vicGroupBy,
        x=df_vicGroupBy.index,
        y='Num_Acc',
        labels={
            "Num_Acc": "Victimes",
            "catv_2": "Catégorie du véhicule"
        },
        title="Victimes selon la catégorie du véhicule",
        text='Num_Acc',
        color_discrete_sequence=COLOR
    )

    # heure-graph --------------------------------
    df_vicGroupBy = df_vic.groupby('heure').count()
    fig13 = px.bar(
        df_vicGroupBy,
        x=df_vicGroupBy.index,
        y='Num_Acc',
        labels={
            "Num_Acc": "Victimes",
            "heure": "Heure"
        },
        title="Victimes selon l'heure",
        text='Num_Acc',
        color_discrete_sequence=COLOR
    )

    # map-graph ----------------------------------
    df_vic['grav'].astype(int)
    fig14 = px.scatter_map(
        df_vic, 
        lat='lat', 
        lon='long', 
        color='grav_2',
        hover_name='com', 
        hover_data=["lat", "long", "date", "hrmn", "catv", "catu", "grav_2", "sexe", "classe_age"],
        labels={"grav_2": "Gravité"},
        height=800,
        color_discrete_map={
            "Tué": "black",
            "Blessé hospitalisé": "red",
            "Blessé léger": "orange"
        },
        title="Cartographie des victimes selon la gravité",
    )
    fig14.update_layout(map_style="open-street-map")
    fig14.update_traces(marker=dict(size=15))

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, fig12, fig13, fig14

# =============================================================
# MAIN APP
# =============================================================

st.set_page_config(page_title="AcciViz", layout="wide")

st.title(":material/car_crash: AcciViz")
st.sidebar.title("Filtres")

with st.expander("À propos"):
    st.markdown(
        f'''  
        **AcciViz** est un tableau de bord permettant de visualier les données d'accidentalité pour un département et une année sélectionnés.

        ### Source des données
        
        Les données accidents utilisées proviennent toutes du site Web [datagouv.fr](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024).
        Elles sont sous licence ouverte ([Open licence](https://www.etalab.gouv.fr/wp-content/uploads/2014/05/Licence_Ouverte.pdf)).

        Les bases de données, extraites du fichier BAAC, répertorient l'intégralité des accidents corporels de la circulation, intervenus durant une année précise en France métropolitaine, dans les départements d'Outre-mer (Guadeloupe, Guyane, Martinique, La Réunion et Mayotte depuis 2012) et dans les autres territoires d'Outre-mer (Saint-Pierre-et-Miquelon, Saint-Barthélemy, Saint-Martin, Wallis-et-Futuna, Polynésie française et Nouvelle-Calédonie ; disponible qu'à partir de 2019 dans l'open data) avec une description simplifiée.
        Cela comprend des informations de localisation de l'accident, telles que renseignées ainsi que des informations concernant les caractéristiques de l'accident et son lieu, les véhicules impliqués et leurs victimes.

        Le terme **victimes** regroupe les usagers tués et les usagers blessés (blessés hospitalisés + blessés légers).
        
        Les base de données de 2005 à 2024 (2025 n'est pas encore disponible en open data) sont désormais annuelles et composées de 4 fichiers au format CSV : Caractéristiques ; Lieux ; Véhicules ; Usagers. Ces 4 fichiers sont fusionnés par l'application **AcciViz** en un seul jeu de données **accidents**. Enfin, ce dernier est utilisé pour créer le tableau de bord.
        '''
    )

    st.image("assets/workflow.png")

    st.markdown(
        '''        
        Pour l'exploitation des données, il est vivement recommandé de télécharger la description des bases de données annuelles.
        '''
    )
    

    with open("assets/description-des-bases-de-donnees-annuelles-1.pdf", "rb") as f:
        pdf_bytes = f.read()

    st.download_button(
        label="Télécharger la description des bases de données (PDF)",
        data=pdf_bytes,
        file_name="description-bdd-annuelles.pdf",
        mime="application/pdf",
        icon=":material/download:",
        type="primary"
    )

    st.markdown(
        '''
        Les données de population proviennent du site Web de l'Insee.
        Chaque année, l'institut estime la population des départements (France métropolitaine et DOM) à la date du 1er janvier ([Insee - Population](https://www.insee.fr/fr/statistiques/8721456)).

        ### Contact
                
        Stéphane SADOWSKI  
        Chargé d'études en sécurité routière  
        Cerema - DTerEst-DTMI-CSI - Bâtiment C Île du Saulcy - 57000 Metz  
        :material/contact_mail: [stephane.sadowski@cerema.fr](mailto:stephane.sadowski@cerema.fr)  
        :material/phone: 01 59 44 39 04 - 07 64 42 87 61
        '''
    )

    c1, c2, c3 = st.columns([0.4, 0.4, 0.2])
    c1.image("assets/logo_cerema_horizontal_resized.png", link="https://www.cerema.fr/fr")
    c2.image("assets/onisr.png", link="https://www.onisr.securite-routiere.gouv.fr/")
    c3.image("assets/securite_ensemble.png", link="https://www.securite-routiere.gouv.fr/")

st.divider()

year = st.sidebar.selectbox("**Année :**", options=(2024, 2023, 2022, 2021, 2020), index=0)
dept = st.sidebar.selectbox("**Département :**", options=[nom_complet for _, _, nom_complet, _ in list_dept()], index=57)
grav = st.sidebar.selectbox("**Gravité :**", options=["Toutes les gravités", "Tués", "Blessés hospitalisés", "Blessés légers"], index=0)

info_dept = get_info_dept(dept)
id_grav = get_id_grav(grav)

df_accident, df_caracteristique, df_lieu, df_vehicule, df_usager = load_data(year, dept, id_grav)
df_accident = prepare_data(df_accident)

st.sidebar.success(f"{df_accident.shape[0]} lignes chargées.", icon=":material/check:")

df_indicateur = calculate_indicators(df_accident)

type_victime = f"Accidentalité des {grav.lower()} " if id_grav != 0 else "Accidentalité "
st.subheader(f"{type_victime}pour l'année {year} dans le département {dept}")

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Nombre d'accidents (A)", 
    value=f'{df_indicateur["Num_Acc"].nunique():n}', 
    delta=f'{int(df_indicateur["Num_Acc"].nunique() * 1e6 / info_dept[3]):n} en Mhab' if info_dept[3] is not None else '-- en Mhab', 
    delta_arrow="off", 
    delta_color="blue", 
    border=True
)
c2.metric(
    "Nombre d'accidents mortels (AM)", 
    value=f'{df_indicateur["AM"].sum():n}', 
    delta=f'{int(df_indicateur["AM"].sum() * 1e6 / info_dept[3]):n} en Mhab' if info_dept[3] is not None else '-- en Mhab',
    delta_arrow="off",
    delta_color="blue",
    border=True
)
c3.metric(
    "Nombre d'accidents graves non mortel (AGNM)", 
    value=f'{df_indicateur["AGNM"].sum():n}',
    delta=f'{int(df_indicateur["AGNM"].sum() * 1e6 / info_dept[3]):n} en Mhab' if info_dept[3] is not None else '-- en Mhab',
    delta_arrow="off",
    delta_color="blue", 
    border=True
)
c4.metric(
    "Nombre d'accidents légers (AL)", 
    value=f'{df_indicateur["AL"].sum():n}',
    delta=f'{int(df_indicateur["AL"].sum() * 1e6 / info_dept[3]):n} en Mhab' if info_dept[3] is not None else '-- en Mhab',
    delta_arrow="off",
    delta_color="blue", 
    border=True
)

c5, c6, c7, c8 = st.columns(4)
c5.metric(
    "Nombre de victimes (V)", 
    value=f'{df_indicateur["T"].astype(int).sum() + df_indicateur["BH"].astype(int).sum() + df_indicateur["BL"].astype(int).sum():n}', 
    delta=f'{int((df_indicateur["T"].astype(int).sum() + df_indicateur["BH"].astype(int).sum() + df_indicateur["BL"].astype(int).sum()) * 1e6 / info_dept[3]):n} en Mhab' if info_dept[3] is not None else '-- en Mhab',
    delta_arrow="off",
    delta_color="blue",
    border=True
)
c6.metric(
    "Nombre de tués (T)", 
    value=f'{df_indicateur["T"].astype(int).sum():n}',
    delta=f'{int(df_indicateur["T"].astype(int).sum() * 1e6 / info_dept[3]):n} en Mhab' if info_dept[3] is not None else '-- en Mhab',
    delta_arrow="off",
    delta_color="blue",
    border=True
)
c7.metric(
    "Nombre de blessés (B)", 
    value=f'{df_indicateur["BH"].astype(int).sum() + df_indicateur["BL"].astype(int).sum():n}',
    delta=f'{int((df_indicateur["BH"].astype(int).sum() + df_indicateur["BL"].astype(int).sum()) * 1e6 / info_dept[3]):n} en Mhab' if info_dept[3] is not None else '-- en Mhab', 
    delta_arrow="off",
    delta_color="blue", 
    border=True
)
c8.metric(
    "Nombre de blessés hospitalisés (H)", 
    value=f'{df_indicateur["BH"].astype(int).sum():n}',
    delta=f'{int(df_indicateur["BH"].astype(int).sum() * 1e6 / info_dept[3]):n} en Mhab' if info_dept[3] is not None else '-- en Mhab',
    delta_arrow="off",
    delta_color="blue", 
    border=True
)

# Conserver uniquement les victimes, écarter les "Indemnes".
df_victimes = df_accident[(df_accident["grav"] == 2) | (df_accident["grav"] == 3) | (df_accident["grav"] == 4)].reset_index()

fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, fig12, fig13, fig14 = generate_graph(df_victimes)

c1, c2, c3 = st.columns(3)

with c1:
    # Part des victimes par catégorie d'usager
    with st.container(border=True):
        st.plotly_chart(fig7)

    # Part des victimes par localisation
    with st.container(border=True):
        st.plotly_chart(fig1)

    # Part des victimes par luminosités
    with st.container(border=True):
        st.plotly_chart(fig3)

with c2:
    # Victimes par sexe
    with st.container(border=True):
        st.plotly_chart(fig8)
    
    # Part des victimes par intersection
    with st.container(border=True):
        st.plotly_chart(fig2)

    # Victimes par conditions atmosphériques
    with st.container(border=True):
        st.plotly_chart(fig5)

with c3:
    # Victimes selon la classe d'âges
    with st.container(border=True):
        st.plotly_chart(fig9)

    # Part des victimes par catégorie de route
    with st.container(border=True):
        st.plotly_chart(fig4)

    # Victimes selon l'état de surface de la chaussée
    with st.container(border=True):
        st.plotly_chart(fig6)

c4, c5 = st.columns(2)

with c4:
    # Victimes par mode de déplacement
    with st.container(border=True):
        st.plotly_chart(fig12)

    # Victimes selon le mois
    with st.container(border=True):
        st.plotly_chart(fig11)

with c5:
    # Victimes par type de trajet
    with st.container(border=True):
        st.plotly_chart(fig10)

    # Victimes selon l'heure
    with st.container(border=True):
        st.plotly_chart(fig13)



with st.container(border=True):
    st.plotly_chart(fig14)

with st.expander("Voir le jeu de données résultat"):
    st.dataframe(df_accident)

    st.sidebar.download_button(
        label="Télécharger le jeu de données",
        data=df_accident.to_csv().encode("utf-8"),
        file_name=f"export_{year}_{dept}.csv",
        mime="text/csv",
        type="primary",
        width="stretch",
        icon=":material/download:"
    )

# =============================================================
# SECTION DE TEST - À SUPPRIMER
# =============================================================


