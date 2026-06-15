import streamlit as st

st.set_page_config(
    page_title="Abhay's Risk Analysis App",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'A personal project by abhaypai@vt.edu',
    }
)

overview = st.Page(
    page = "pages/Overview.py",
    title = "KPIs",
    default = True
)

correlation = st.Page(
    page = "pages/Correlation.py",
    title = "Variable Correlation",
)

economic = st.Page(
    page = "pages/Economic.py",
    title = "Economic Indicators",
)

segmentation = st.Page(
    page = "pages/Segmentation.py",
    title = "Segmentation",
)

st.markdown(
    """
    <style>
        .main-header {
            font-size:32px !important;
            font-weight:600;
            padding-bottom:10px;
            padding-top:5px;
            border-bottom: 1px solid #eee;
        }
    </style>
    """, unsafe_allow_html=True
)

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


pg=st.navigation(
    {
        "Dashboard":[overview],
        'Analytics':[segmentation],
        'Additional Charts': [economic, correlation]
    })

st.sidebar.text("Made by Abhay Pai")
st.sidebar.text("(@abhaypaii)")

pg.run()
