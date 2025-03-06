import streamlit as st

def main():
    # Configuration de la page (nom, layout, etc.)
    # Utilise un thème "de base" pour spécifier les couleurs principales
    st.set_page_config(
        page_title="Dynamic Hedger",
        layout="wide",
        page_icon=":chart_with_upwards_trend:"
    )


    # -- Personnalisation supplémentaire par CSS --
    # Ici, on précise un fond de sidebar et de la page,
    # ainsi qu'une éventuelle couleur d'accent (#E3B505) si besoin.
    st.markdown(
        f"""
        <style>
        /* Couleur de fond principale de l'application */
        [data-testid="stAppViewContainer"] {{
            background-color: #FAFAFF;
            color: black;
        }}

        /* Couleur de fond de la sidebar */
        [data-testid="stSidebar"] > div:first-child {{
            background-color: #ECECFF;
        }}

        /* Exemple: si vous souhaitez utiliser #E3B505 pour des titres/accents spécifiques,
           vous pouvez cibler des classes ou des éléments particuliers. Ex : */
        h1, h2, h3 {{
            /* Exemple d'utilisation d'une couleur d'accent */
            color: #131CC9;
        }}

        /* Vous pouvez aussi ajouter d'autres règles de style selon vos préférences */
        </style>
        """,
        unsafe_allow_html=True
    )

    # Titre principal de votre application
    st.title("Dynamic Hedger")

    # Création d'un menu latéral
    st.sidebar.title("Menu")
    menu = st.sidebar.radio(
        "Navigation",
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
