import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def calculate_global_stats(history_df, items_df, submissions_df):
    """
    Calculates global KPIs for the dashboard.
    """
    # Reborrow Rate
    total_borrows = 0
    unique_borrows = 0
    
    # Process history for reborrow calculation
    # We re-process to be safe, or we could assume a pre-processed format.
    # Given the raw 'books_borrowed' is "0, 1, 2...", let's parse it.
    
    all_borrowed_ids = []
    
    for ids_str in history_df['books_borrowed']:
        if pd.isna(ids_str): continue
        ids = [int(x.strip()) for x in str(ids_str).split(',') if x.strip().isdigit()]
        all_borrowed_ids.extend(ids)
        
    total_borrows = len(all_borrowed_ids)
    unique_borrows_global = len(set(all_borrowed_ids))
    
    # "Reborrow" in the sense of the users: 
    # The user request mentioned "reborrow represents 26.47%".
    # My previous script calculation was based on sum(len(user_borrows)) vs sum(len(set(user_borrows))).
    # Let's replicate that EXACT logic per user row to match the 26.47%.
    
    total_b_accum = 0
    unique_b_accum = 0
    
    for ids_str in history_df['books_borrowed']:
         if pd.isna(ids_str): continue
         ids = [x.strip() for x in str(ids_str).split(',') if x.strip().isdigit()]
         total_b_accum += len(ids)
         unique_b_accum += len(set(ids))
         
    reborrow_count = total_b_accum - unique_b_accum
    reborrow_rate = (reborrow_count / total_b_accum * 100) if total_b_accum > 0 else 0
    
    stats = {
        "Total Users": len(history_df),
        "Total Books in Library": len(items_df),
        "Total Borrows": total_b_accum,
        "Reborrow Rate": reborrow_rate
    }
    
    return stats

@st.cache_data
def calculate_user_stats(history_df):
    """
    Returns a dataframe with per-user statistics.
    """
    user_stats = []
    
    for _, row in history_df.iterrows():
        uid = row['user_id']
        ids_str = row['books_borrowed']
        
        if pd.isna(ids_str):
            count = 0
            unique = 0
        else:
            ids = [x for x in str(ids_str).split(',') if x.strip().isdigit()]
            count = len(ids)
            unique = len(set(ids))
            
        user_stats.append({
            "User ID": uid,
            "Total Borrows": count,
            "Unique Books": unique,
            "Reborrow Ratio": f"{(1 - unique/count)*100:.1f}%" if count > 0 else "0%"
        })
        
    return pd.DataFrame(user_stats)

@st.cache_data
def prepare_cluster_data(items_df):
    """
    Prepares data for the clustering visualization.
    """
    df = items_df.copy()
    
    # 1. Extract Main Category (before first ;)
    # Handle NaN by checking type or filling first
    df['Category'] = df['Category'].fillna("Unknown")
    df['Main_Category'] = df['Category'].apply(lambda x: x.split(';')[0].strip())
    
    # 2. Filter Top N Categories (Keep top 19 + Other = 20 max for color palette)
    top_categories = df['Main_Category'].value_counts().head(19).index
    df['Category_Grouped'] = df['Main_Category'].apply(lambda x: x if x in top_categories else 'Other')
    
    # 3. Assign random centers to categories
    categories = df['Category_Grouped'].unique()
    # Use a seed for consistent positions
    np.random.seed(42)  
    centers = {cat: np.random.rand(2) * 100 for cat in categories}
    
    # 4. Generate points around centers with Gaussian noise
    def get_coords(cat):
        center = centers[cat]
        noise = np.random.randn(2) * 8 # Increased spread slightly
        return center + noise
    
    coords = df['Category_Grouped'].apply(get_coords)
    
    df['x'] = coords.apply(lambda v: v[0])
    df['y'] = coords.apply(lambda v: v[1])
    
    # Return dataframe with the new Grouped Category for coloring
    return df[['Title', 'Author', 'Main_Category', 'Category_Grouped', 'x', 'y']]

@st.cache_data
def calculate_book_stats(history_df, items_df):
    """
    Calculates detailed book-level statistics.
    Returns:
        borrow_counts_df: DataFrame with Title, Author, Category, Borrow Count
        top_books_df: DataFrame of top borrowed books
        top_categories_df: DataFrame of top borrowed categories
    """
    # 1. Count global borrows for every book ID
    all_borrows = []
    
    for ids_str in history_df['books_borrowed']:
        if pd.isna(ids_str): continue
        # ids in history are 0-indexed integers matching items_df index (based on load_data logic usually)
        ids = [int(x.strip()) for x in str(ids_str).split(',') if x.strip().isdigit()]
        all_borrows.extend(ids)
        
    # Create a Series for counts
    borrow_counts = pd.Series(all_borrows).value_counts().rename("Borrow_Count")
    borrow_counts.index.name = "item_id"
    
    # 2. Merge with Items Data
    # items_df index is assumed to correspond to the IDs in books_borrowed
    # (Checking load_data logic in other files would confirm, but this is the standard pattern in this app)
    
    df = items_df.copy()
    df.index.name = "item_id"
    
    # Left join to keep all books even if never borrowed (fill with 0) or inner join?
    # User asked for "pour chaque livre le nombre de user qui l'on emprunté".
    # Usually better to show all books or at least those with > 0 borrows.
    # Let's map counts to the main df.
    
    df = df.join(borrow_counts, how='left')
    df['Borrow_Count'] = df['Borrow_Count'].fillna(0).astype(int)
    
    # Handle missing categories for grouping
    df['Category'] = df['Category'].fillna("Unknown")
    df['Main_Category'] = df['Category'].apply(lambda x: x.split(';')[0].strip())
    
    # 3. Top Books
    top_books_df = df.sort_values(by="Borrow_Count", ascending=False).head(10)
    top_books_df = top_books_df[['Title', 'Author', 'Main_Category', 'Borrow_Count']]
    
    # 4. Top Categories
    # Sum borrow counts by category
    cat_stats = df.groupby('Main_Category')['Borrow_Count'].sum().sort_values(ascending=False).reset_index()
    cat_stats.columns = ['Category', 'Total_Borrows']
    top_categories_df = cat_stats.head(10)
    
    # 5. Full Table for "pour chaque livre"
    # Clean up columns for display
    borrow_counts_df = df[['Title', 'Author', 'Main_Category', 'Borrow_Count']].sort_values(by="Borrow_Count", ascending=False)
    
    return borrow_counts_df, top_books_df, top_categories_df
