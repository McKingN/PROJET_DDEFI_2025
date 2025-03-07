import streamlit as st
from PIL import Image

def main():
    # Chemin vers votre logo
    logo_path = "C:\\Users\\McKing.DESKTOP-4Q7G3QP\\Documents\\GitHub\\3A Marseille\\PROJET_DDEFI_2025\\app\\images\\O.png"  
    # Charger le logo avec Pillow
    logo_image = Image.open(logo_path)
    
    # Configurer la page avec le logo comme icône
    st.set_page_config(
        page_title="OptiHedge App",
        layout="wide",
        page_icon=logo_image
    )

    # Personnalisation supplémentaire par CSS avec une police agrandie
    st.markdown(
        f"""
        <style>
        /* Appliquer une taille de police agrandie à l'ensemble de l'application */
        body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
            font-size: 18px;
        }}

        /* Couleur de fond principale de l'application */
        [data-testid="stAppViewContainer"] {{
            background-color: #FAFAFF;
            color: black;
        }}

        /* Couleur de fond de la sidebar */
        [data-testid="stSidebar"] > div:first-child {{
            background-color: #ECECFF;
        }}

        /* Exemple: utilisation d'une couleur d'accent pour les titres avec une taille de police augmentée */
        h1 {{
            color: #131CC9;
            font-size: 2.5em;
        }}
        h2, h3 {{
            color: #131CC9;
            font-size: 2em;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Titre principal de l'application
    st.title("OptiHedge")

    # Afficher le logo dans la sidebar avec use_container_width
    st.sidebar.image(logo_image, use_container_width=True)

    # Création du menu latéral
    st.sidebar.title("Menu")
    menu = st.sidebar.radio(
        "Mon espace",
        ("Accueil", "Hedger", "Backtesting", "FAQ")
    )

    # Navigation vers les différentes pages
    if menu == "Accueil":
        import accueil
        accueil.show()
    elif menu == "Hedger":
        import hedger
        hedger.show()
    elif menu == "Backtesting":
        import backtesting
        backtesting.show()
    elif menu == "FAQ":
        import faq
        faq.show()

if __name__ == "__main__":
    main()
