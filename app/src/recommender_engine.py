import pandas as pd
import streamlit as st
from .statistics import calculate_book_stats

@st.cache_data
def get_category_recommendations(history_df, items_df):
    """
    Pre-calculates top books for every category to be used in client-side JS recommender.
    Returns:
        category_recs: Dict { "CategoryName": [ {Title, Author}, ... ] }
        all_categories: List of sorted category names
    """
    # Reuse existing stats logic to get popularity
    # borrow_counts_df has columns: Title, Author, Main_Category, Borrow_Count
    borrow_counts_df, _, _ = calculate_book_stats(history_df, items_df)
    
    # Filter only relevant columns to save space
    df = borrow_counts_df[['Title', 'Author', 'Main_Category', 'Borrow_Count']]
    
    # Group by Category and get Top 20 per category
    # (We only need top 10 max for the UI, but 20 gives variety if we add randomness later)
    category_recs = {}
    
    # Get list of unique categories
    categories = df['Main_Category'].unique()
    
    for cat in categories:
        # Get top books for this category
        top_books = df[df['Main_Category'] == cat].head(20)
        
        # Convert to list of dicts
        books_list = top_books[['Title', 'Author']].to_dict('records')
        category_recs[cat] = books_list
        
    all_categories = sorted(list(category_recs.keys()))
    
    return category_recs, all_categories
