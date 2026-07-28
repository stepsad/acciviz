import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


@st.cache_data
def load_data(year=2024, dept='57 Moselle'):
    df_caracteristique = pd.read_csv(f"data/caracteristiques-{year}.csv", sep=";")
    df_lieu = pd.read_csv(f"data/lieux-{year}.csv", sep=";", low_memory=False)
    df_vehicule = pd.read_csv(f"data/vehicules-{year}.csv", sep=";")
    df_usager = pd.read_csv(f"data/usagers-{year}.csv", sep=";")

    code_dept = dept.split(sep=" ")
    df_caracteristique = df_caracteristique[df_caracteristique["dep"] == code_dept[0]]

    df_lieu = df_lieu.sort_values(["Num_Acc", "catr"])
    df_lieu = df_lieu.drop_duplicates(subset="Num_Acc", keep="first")

    df_accident = pd.merge(df_caracteristique, df_lieu, how="left", on="Num_Acc")
    df_accident = pd.merge(df_accident, df_vehicule, how="left", on="Num_Acc")
    df_accident = pd.merge(df_accident, df_usager, how="left", on=["Num_Acc", "id_vehicule"])   

    return df_accident, df_caracteristique, df_lieu, df_vehicule, df_usager

def preparer_df(df_accident):
    # Caster les colonnes 'lat' et 'long' en entier
    df_accident['lat'] = df_accident['lat'].str.replace(',', '.')
    df_accident['long'] = df_accident['long'].str.replace(',', '.')
    df_accident[['lat', 'long']] = df_accident[['lat', 'long']].apply(pd.to_numeric)

    # Ajouter une colonne 'date'
    df_accident = df_accident.assign(date = 'NA')
    df_accident['date'] = df_accident['an'].map(str) + "-" + df_accident['mois'].map(str) + "-" + df_accident['jour'].map(str)
    df_accident['date'] = pd.to_datetime(df_accident['date'])

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

    # Ajouter une colonne 'grav_2'
    df_accident = df_accident.assign(grav_2 = 'Indemne')
    df_accident.loc[df_accident.grav == 2, 'grav_2'] = 'Tué'
    df_accident.loc[df_accident.grav == 3, 'grav_2'] = 'Blessé hospitalisé'
    df_accident.loc[df_accident.grav == 4, 'grav_2'] = 'Blessé léger'

    # Ajouter une colonne 'age'
    df_accident = df_accident.assign(age = '0-17')
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 17, 'age'] = '18-24'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 24, 'age'] = '25-34'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 34, 'age'] = '35-44'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 44, 'age'] = '45-54'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 54, 'age'] = '55-64'
    df_accident.loc[(df_accident.an - df_accident.an_nais) > 64, 'age'] = '65+'

    # Ajouter une colonne 'lum_2'
    df_accident = df_accident.assign(lum_2 = 'Jour')
    df_accident.loc[df_accident.lum == 3, 'lum_2'] = 'Nuit'
    df_accident.loc[df_accident.lum == 4, 'lum_2'] = 'Nuit'
    df_accident.loc[df_accident.lum == 5, 'lum_2'] = 'Nuit'

    return df_accident

def calculer_indicateurs(df):
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

def lister_departement():
    # Métropole (01–95, + 2A, 2B pour la Corse)
    metro = [
        "01 Ain", "02 Aisne", "03 Allier", "04 Alpes-de-Haute-Provence",
        "05 Hautes-Alpes", "06 Alpes-Maritimes", "07 Ardèche", "08 Ardennes",
        "09 Ariège", "10 Aube", "11 Aude", "12 Aveyron", "13 Bouches-du-Rhône",
        "14 Calvados", "15 Cantal", "16 Charente", "17 Charente-Maritime",
        "18 Cher", "19 Corrèze", "21 Côte-d'Or", "22 Côtes-d'Armor",
        "23 Creuse", "24 Dordogne", "25 Doubs", "26 Drôme", "27 Eure",
        "28 Eure-et-Loir", "29 Finistère", "2A Corse-du-Sud", "2B Haute-Corse",
        "30 Gard", "31 Haute-Garonne", "32 Gers", "33 Gironde", "34 Hérault",
        "35 Ille-et-Vilaine", "36 Indre", "37 Indre-et-Loire", "38 Isère",
        "39 Jura", "40 Landes", "41 Loir-et-Cher", "42 Loire", "43 Haute-Loire",
        "44 Loire-Atlantique", "45 Loiret", "46 Lot", "47 Lot-et-Garonne",
        "48 Lozère", "49 Maine-et-Loire", "50 Manche", "51 Marne", "52 Haute-Marne",
        "53 Mayenne", "54 Meurthe-et-Moselle", "55 Meuse", "56 Morbihan",
        "57 Moselle", "58 Nièvre", "59 Nord", "60 Oise", "61 Orne", "62 Pas-de-Calais",
        "63 Puy-de-Dôme", "64 Pyrénées-Atlantiques", "65 Hautes-Pyrénées",
        "66 Pyrénées-Orientales", "67 Bas-Rhin", "68 Haut-Rhin", "69 Rhône",
        "70 Haute-Saône", "71 Saône-et-Loire", "72 Sarthe", "73 Savoie",
        "74 Haute-Savoie", "75 Paris", "76 Seine-Maritime", "77 Seine-et-Marne",
        "78 Yvelines", "79 Deux-Sèvres", "80 Somme", "81 Tarn", "82 Tarn-et-Garonne",
        "83 Var", "84 Vaucluse", "85 Vendée", "86 Vienne", "87 Haute-Vienne",
        "88 Vosges", "89 Yonne", "90 Territoire-de-Belfort", "91 Essonne",
        "92 Hauts-de-Seine", "93 Seine-Saint-Denis", "94 Val-de-Marne", "95 Val-d'Oise",
    ]

    # DOM-TOM (DROM + COM principaux)
    domtom = [
        "971 Guadeloupe",
        "972 Martinique",
        "973 Guyane",
        "974 La Réunion",
        "976 Mayotte",
        "975 Saint-Pierre-et-Miquelon",
        "977 Saint-Barthélemy",
        "978 Saint-Martin",
        "986 Wallis-et-Futuna",
        "987 Polynésie française",
        "988 Nouvelle-Calédonie",
    ]

    return metro + domtom    


# =============================================================
# MAIN APP
# =============================================================

st.set_page_config(page_title="AcciViz", layout="wide")

st.title(":material/car_crash: AcciViz")

with st.expander("À propos"):
    st.markdown(
        '''
        **AcciViz** est un tableau de bord permettant de visualier l'accidentalité d'un département pour une année sélectionnée.

        ### Source des données
        
        Les données accidents proviennent toutes du site Web [datagouv.fr](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024).
        Elles sont sous licence ouverte (Open licence).
        
        Pour l'exploitation du jeu de données, il est vivement recommandé de télécharger la description des bases de données annuelles.
        '''
    )

    with open("assets/description-des-bases-de-donnees-annuelles-1.pdf", "rb") as f:
        pdf_bytes = f.read()

    st.download_button(
        label="Télécharger la description des bases de données (PDF)",
        data=pdf_bytes,
        file_name="description-bdd-annuelles.pdf",
        mime="application/pdf",
        icon=":material/download:"
    )

    st.markdown(
        '''
        ### Contact
                
        Stéphane SADOWSKI  
        Chargé d'études en sécurité routière  
        Cerema Est - Bâtiment C Île du Saulcy - 57000 Metz  
        :material/contact_mail: [stephane.sadowski@cerema.fr](mailto:stephane.sadowski@cerema.fr)  
        :material/phone: 07 64 42 87 61
        '''
    )

    c1, c2, c3 = st.columns([0.4, 0.4, 0.2])
    c1.image("assets/logo_cerema_horizontal_resized.png", link="https://www.cerema.fr/fr")
    c2.image("assets/onisr.png", link="https://www.onisr.securite-routiere.gouv.fr/")
    c3.image("assets/securite_ensemble.png", link="https://www.securite-routiere.gouv.fr/")

st.divider()

year = st.sidebar.selectbox("**Année :**", options=(2024, 2023, 2022, 2021, 2020), index=0)
dept = st.sidebar.selectbox("**Code Insee département :**", options=lister_departement(), index=57)

df_accident, df_caracteristique, df_lieu, df_vehicule, df_usager = load_data(year, dept)
df_accident = preparer_df(df_accident)

st.sidebar.success(f"{df_accident.shape[0]} lignes chargées.", icon=":material/check:")

df_indicateur = calculer_indicateurs(df_accident)

st.subheader(f"Accidentologie pour l'année {year} dans le département {dept}")

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Nombre d'accidents (A)", 
    value=df_indicateur["Num_Acc"].nunique(), 
    delta=f'{int(df_indicateur["Num_Acc"].nunique() * 1e6 / 1051309)} en Mhab', 
    delta_arrow="off", 
    delta_color="off", 
    border=True
)
c2.metric(
    "Nombre d'accidents mortels (AM)", 
    value=df_indicateur["AM"].sum(), 
    border=True
)
c3.metric(
    "Nombre d'accidents graves non mortel (AGNM)", 
    value=df_indicateur["AGNM"].sum(), 
    border=True
)
c4.metric(
    "Nombre d'accidents légers (AL)", 
    value=df_indicateur["AL"].sum(), 
    border=True
)

c5, c6, c7, c8 = st.columns(4)
c5.metric(
    "Nombre de victimes (V)", 
    value=df_indicateur["T"].astype(int).sum() + df_indicateur["BH"].astype(int).sum() + df_indicateur["BL"].astype(int).sum(), 
    border=True
)
c6.metric(
    "Nombre de tués (T)", 
    value=df_indicateur["T"].astype(int).sum(), 
    border=True
)
c7.metric(
    "Nombre de blessés (B)", 
    value=df_indicateur["BH"].astype(int).sum() + df_indicateur["BL"].astype(int).sum(), 
    border=True
)
c8.metric(
    "Nombre de blessés hospitalisés (H)", 
    value=df_indicateur["BH"].astype(int).sum(), 
    border=True
)

# Conserver uniquement les victimes, écarter les "Indemnes".
df_victimes = df_accident[(df_accident["grav"] == 2) | (df_accident["grav"] == 3) | (df_accident["grav"] == 4)].reset_index()

c1, c2, c3 = st.columns(3)

with c1:
    # Part des victimes par localisation
    with st.container(border=True):
        df_victimesByAgg2 = df_victimes.groupby('agg_2').count()
        fig1 = px.pie(
            df_victimesByAgg2, 
            values="Num_Acc", 
            names=df_victimesByAgg2.index,
            labels={
                "Num_Acc": "Victimes",
                "agg_2": "Localisation"
            }, 
            title="Part des victimes par localisation",
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )
        st.plotly_chart(fig1)

    # Part des victimes par catégorie de route
    with st.container(border=True):
        df_victimesByCatr2 = df_victimes.groupby('catr_2').count()
        fig4 = px.bar(
            df_victimesByCatr2,
            x=df_victimesByCatr2.index,
            y='Num_Acc',
            labels={
                "Num_Acc": "Victimes",
                "catr_2": "Cat. route"
            },
            title="Victimes par catégorie de route",
            text='Num_Acc',
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )
        st.plotly_chart(fig4)

    # Part des victimes par catégorie d'usager
    with st.container(border=True):
        df_victimesByCatu = df_victimes.groupby('catu').count()
        df_victimesByCatu.rename(index={1: 'Conducteur', 2: 'Passager', 3: 'Piéton'}, inplace=True)
        fig7 = px.pie(
            df_victimesByCatu, 
            values="Num_Acc", 
            names=df_victimesByCatu.index,
            labels={
                "Num_Acc": "Victimes",
                "catu": "Cat. usager"
            }, 
            title="Part des victimes par catégorie d'usager",
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )
        st.plotly_chart(fig7)


with c2:
    # Part des victimes par intersection
    with st.container(border=True):
        df_victimesByInt2 = df_victimes.groupby('int_2').count()
        fig2 = px.pie(
            df_victimesByInt2, 
            values="Num_Acc", 
            names=df_victimesByInt2.index,
            labels={
                "Num_Acc": "Victimes",
                "int_2": "Intersection"
            }, 
            title="Part des victimes par intersection",
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )
        st.plotly_chart(fig2)

    # Victimes par conditions atmosphériques
    with st.container(border=True):
        df_victimesByAtm2 = df_victimes.groupby('atm_2').count()
        fig5 = px.bar(
            df_victimesByAtm2,
            x=df_victimesByAtm2.index,
            y='Num_Acc',
            labels={
                "Num_Acc": "Victimes",
                "atm_2": "Cond. atmosphériques"
            },
            title="Victimes par conditions atmosphériques",
            text='Num_Acc',
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )
        st.plotly_chart(fig5)


with c3:
    # Part des victimes par luminosités
    with st.container(border=True):
        df_victimesByLum2 = df_victimes.groupby('lum_2').count()
        fig3 = px.pie(
            df_victimesByLum2, 
            values="Num_Acc", 
            names=df_victimesByLum2.index,
            labels={
                "Num_Acc": "Victimes",
                "lum_2": "Luminosité"
            }, 
            title="Part des victimes par luminosité",
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )
        st.plotly_chart(fig3)

    # Victimes selon l'état de surface de la chaussée
    with st.container(border=True):
        df_victimesBySurf2 = df_victimes.groupby('surf_2').count()
        fig6 = px.bar(
            df_victimesBySurf2,
            x=df_victimesBySurf2.index,
            y='Num_Acc',
            labels={
                "Num_Acc": "Victimes",
                "surf_2": "Etat surface"
            },
            title="Victimes selon l'état de surface de la chaussée",
            text='Num_Acc',
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )
        st.plotly_chart(fig6)


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



