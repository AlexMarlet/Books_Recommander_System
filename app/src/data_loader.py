
import pandas as pd
import json
import streamlit as st
from .config import SUBMISSION_PATH, ITEMS_ENRICHED_PATH, USER_HISTORY_PATH, DEMO_USER_LIMIT

@st.cache_data
def load_data():
    """
    Loads usage and recommendation data from CSV files.
    """
    submissions = pd.read_csv(SUBMISSION_PATH)
    items = pd.read_csv(ITEMS_ENRICHED_PATH)
    history = pd.read_csv(USER_HISTORY_PATH)
    
    # Create lookup dict for items: i -> {Title, Author}
    # Handle NaN values gracefully
    items['Title'] = items['Title'].fillna("Unknown Title")
    items['Author'] = items['Author'].fillna("Unknown Author")
    items_dict = items.set_index('i')[['Title', 'Author']].to_dict('index')
    
    return submissions, history, items_dict

def get_demo_users_json(submissions_df, history_df, items_map):
    """
    Prepares a JSON string containing data for the first N users 
    to be injected into the frontend.
    """
    # Filter for first N users
    all_user_ids = sorted(submissions_df['user_id'].unique())
    demo_users_ids = all_user_ids
    
    users_data = {}

    for uid in demo_users_ids:
        # User History
        user_history_row = history_df[history_df['user_id'] == uid]
        history_books = []
        if not user_history_row.empty:
            # Parse '0, 1, 2' string
            b_ids_str = user_history_row.iloc[0]['books_borrowed']
            if isinstance(b_ids_str, str):
                b_ids = [int(x.strip()) for x in b_ids_str.split(',') if x.strip().isdigit()]
                for bid in b_ids:
                    if bid in items_map:
                        history_books.append(items_map[bid])
        
        # Recommendations
        user_rec_row = submissions_df[submissions_df['user_id'] == uid]
        rec_books = []
        if not user_rec_row.empty:
            # Parse '123 456 789' string (space separated)
            r_str = user_rec_row.iloc[0]['recommendation']
            if isinstance(r_str, str):
                r_ids = [int(x.strip()) for x in r_str.split(' ') if x.strip().isdigit()]
                for rid in r_ids:
                    if rid in items_map:
                        rec_books.append(items_map[rid])
                        
        users_data[int(uid)] = {
            "history": history_books, 
            "recommendations": rec_books 
        }

    return json.dumps(users_data)
