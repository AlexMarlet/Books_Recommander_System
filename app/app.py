import streamlit as st
import streamlit.components.v1 as components
from src.data_loader import load_data, get_demo_users_json
from src.book_renderer import generate_book_html
from src.config import COMPONENT_HEIGHT
from src.statistics import calculate_global_stats, calculate_user_stats, prepare_cluster_data, calculate_book_stats
from src.recommender_engine import get_category_recommendations
from src.views import render_data_insights

st.set_page_config(page_title="Magic Book Animation", layout="wide")

def main():
    # 1. Load Data
    submissions, history, items_map = load_data()
    
    # Navigation
    with st.sidebar:
        st.header("Navigation")
        view_mode = st.radio("Choose User Experience:", 
                             ["Interactive Book", "Data Insights"])
    
    # CSS: Sidebar Width & Conditional Margins
    # Reduce sidebar width to ~250px (default is wider)
    # Conditional padding for main content
    sidebar_css = """
<style>
section[data-testid="stSidebar"] {
    width: 250px !important;
}
</style>
"""
    
    if view_mode == "Interactive Book":
        # Immersive mode: 0 padding
        st.markdown(sidebar_css + """
<style>
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}
</style>
""", unsafe_allow_html=True)
        
        # 2. Prepare JSON for Frontend (Demo Users)
        users_json = get_demo_users_json(submissions, history, items_map)
        
        # 3. Prepare Recommendation Data
        # Calculate on the fly or load. Since it uses cache, it's fast.
        from src.data_loader import ITEMS_ENRICHED_PATH
        import pandas as pd
        import json
        items_df = pd.read_csv(ITEMS_ENRICHED_PATH)
        
        cat_recs, all_cats = get_category_recommendations(history, items_df)
        cat_recs_json = json.dumps(cat_recs)
        
        # 4. Generate HTML
        book_html = generate_book_html(users_json, cat_recs_json, all_cats)
        
        # 4. Render
        components.html(book_html, height=COMPONENT_HEIGHT, scrolling=False)
        
    elif view_mode == "Data Insights":
        # Dashboard mode: Standard padding for better readability
        st.markdown(sidebar_css + """
<style>
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    padding-left: 5rem !important;
    padding-right: 5rem !important;
    max-width: 100% !important;
}
</style>
""", unsafe_allow_html=True)
        
        # Calculate Stats
        from src.data_loader import ITEMS_ENRICHED_PATH
        import pandas as pd
        items_df = pd.read_csv(ITEMS_ENRICHED_PATH) 
        
        g_stats = calculate_global_stats(history, items_df, submissions)
        u_stats = calculate_user_stats(history)
        c_data = prepare_cluster_data(items_df)
        b_stats = calculate_book_stats(history, items_df)
        
        render_data_insights(g_stats, u_stats, c_data, b_stats)

if __name__ == "__main__":
    main()
