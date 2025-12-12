"""
ALL-IN-ONE DATA ENRICHMENT & CLEANING PIPELINE
Consolidates ALL data cleaning and enrichment steps into a single script.
Includes API-based enrichment for ISBNs, Authors, Categories, and Dates.

Flow:
1. Process Interactions (Create History Files)
2. Load Original Items (items.csv)
3. Fix ISBNs (Format cleanup)
4. Find Missing ISBNs (API: Google Books + OpenLibrary)
5. Clean Subjects (Formatting)
6. Create Categories (Map Subjects -> Categories)
7. Find Missing Categories (API)
8. Find Missing Authors (API)
9. Find Missing Dates (API)
10. Extract Years (Final Parsing)
11. Save Enriched Items (items_enriched.csv)

Usage:
    python all_in_one_enrichment.py
"""

import pandas as pd
import numpy as np
import re
import requests
import time
from datetime import datetime
import os

# CONFIGURATION
BASE_DIR = '/Users/alexandrecagnin/Kaggle_datas'
ORIGINAL_DIR = os.path.join(BASE_DIR, 'original_df')

INTERACTIONS_FILE = os.path.join(ORIGINAL_DIR, 'interactions.csv')
ITEMS_FILE = os.path.join(ORIGINAL_DIR, 'items.csv')

# Output Files
USER_HISTORY_FILE = os.path.join(BASE_DIR, 'user_borrowing_history.csv')
BOOK_HISTORY_FILE = os.path.join(BASE_DIR, 'book_user_history.csv')
ITEMS_ENRICHED_FILE = os.path.join(BASE_DIR, 'items_enriched.csv')

# API Keys & Headers
GOOGLE_API_KEY = "AIzaSyAHzrzRD81oo7CaCJtZURwEO0brIPwGi1w" # From implemented_miss_isbn
OPEN_LIBRARY_HEADERS = {'User-Agent': 'BookSearchScript/1.0 (alexandre.marlet@unil.ch)'}

# PART 1: PROCESS INTERACTIONS
def process_interactions():
    print("\n[PART 1] Processing Interactions...")
    
    if not os.path.exists(INTERACTIONS_FILE):
        print(f"Error: {INTERACTIONS_FILE} not found.")
        return

    interactions_df = pd.read_csv(INTERACTIONS_FILE)
    print(f"  Loaded {len(interactions_df):,} interactions")

    # Convert Timestamp
    print("  Converting timestamps...")
    interactions_df['date'] = pd.to_datetime(interactions_df['t'], unit='s')
    interactions_df['date_formatted'] = interactions_df['date'].dt.strftime('%d-%m-%Y')

    # Create User History
    print("  Creating user borrowing history...")
    user_history = interactions_df.sort_values(['u', 't']).copy()
    user_borrowing_history = user_history.groupby('u').agg({
        'i': lambda x: ', '.join(map(str, x)),
        'date_formatted': lambda x: ', '.join(x)
    }).reset_index()
    user_borrowing_history.columns = ['user_id', 'books_borrowed', 'dates_borrowed']
    user_borrowing_history['total_books'] = user_history.groupby('u').size().values
    
    user_borrowing_history.to_csv(USER_HISTORY_FILE, index=False)
    print(f"  ✓ Saved {USER_HISTORY_FILE}")

    # Create Book History
    print("  Creating book user history...")
    book_history = interactions_df.sort_values(['i', 't']).copy()
    book_user_history = book_history.groupby('i').agg({
        'u': lambda x: ', '.join(map(str, x)),
        'date_formatted': lambda x: ', '.join(x)
    }).reset_index()
    book_user_history.columns = ['book_id', 'users_borrowed', 'dates_borrowed']
    book_user_history['total_borrows'] = book_history.groupby('i').size().values
    
    book_user_history.to_csv(BOOK_HISTORY_FILE, index=False)
    print(f"  ✓ Saved {BOOK_HISTORY_FILE}")

# PART 2: ENRICH ITEMS PIPELINE
def enrich_items():
    print("\n[PART 2] Enriching Items Pipeline...")
    
    if not os.path.exists(ITEMS_FILE):
        print(f"Error: {ITEMS_FILE} not found.")
        return

    # 1. LOAD ORIGINAL DATA
    print("  1. Loading original items.csv...")
    items_df = pd.read_csv(ITEMS_FILE)
    print(f"     Loaded {len(items_df):,} items")

    # 2. FIX ISBNs (First Pass - Cleanup)
    print("  2. Fixing ISBNs (Cleanup)...")
    def clean_isbn_format(isbn):
        if pd.isna(isbn): return None
        isbn_str = str(isbn)
        # Handle multiple ISBNs separated by ;
        if ';' in isbn_str:
            isbn_str = isbn_str.split(';')[0].strip()
        # Remove .0
        if isbn_str.endswith('.0'):
            isbn_str = isbn_str[:-2]
        # Keep only digits
        digits = ''.join(filter(str.isdigit, isbn_str))
        if len(digits) >= 10: return digits
        return None

    items_df['ISBN Valid'] = items_df['ISBN Valid'].apply(clean_isbn_format)

    # 3. FIND MISSING ISBNs (API)
    print("  3. Finding Missing ISBNs (API)...")
    missing_isbn_mask = items_df['ISBN Valid'].isna()
    books_missing_isbn = items_df[missing_isbn_mask].copy()
    
    if len(books_missing_isbn) > 0:
        print(f"     Searching for {len(books_missing_isbn)} missing ISBNs...")
        
        def search_google_isbn(title, author):
            try:
                query = f"intitle:{title}"
                if pd.notna(author): query += f" inauthor:{author}"
                url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_API_KEY}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "items" in data:
                        identifiers = data["items"][0]["volumeInfo"].get("industryIdentifiers", [])
                        for identifier in identifiers:
                            if identifier["type"] == "ISBN_13": return identifier["identifier"]
                        for identifier in identifiers:
                            if identifier["type"] == "ISBN_10": return identifier["identifier"]
            except: pass
            return None

        def search_openlibrary_isbn(title, author):
            try:
                url = "https://openlibrary.org/search.json"
                params = {'title': title, 'limit': 1, 'fields': 'isbn'}
                if pd.notna(author): params['author'] = author
                response = requests.get(url, params=params, headers=OPEN_LIBRARY_HEADERS, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("docs"):
                        isbns = data["docs"][0].get("isbn", [])
                        for isbn in isbns:
                            if len(str(isbn)) == 13: return isbn
                        if isbns: return isbns[0]
            except: pass
            return None

        found_count = 0
        for idx, row in books_missing_isbn.iterrows():
            title = str(row['Title']).split('/')[0].strip()
            author = str(row['Author']).split(',')[0].strip() if pd.notna(row['Author']) else None
            
            isbn = search_google_isbn(title, author)
            if not isbn:
                time.sleep(0.5)
                isbn = search_openlibrary_isbn(title, author)
            
            if isbn:
                items_df.at[idx, 'ISBN Valid'] = isbn
                found_count += 1
                if found_count % 10 == 0: print(f"     Found {found_count} ISBNs...")
            
            time.sleep(0.5)
        print(f"     Found {found_count} new ISBNs")
    else:
        print("     No missing ISBNs.")

    # 4. CLEAN SUBJECTS
    print("  4. Cleaning Subjects...")
    items_df['Subjects'] = items_df['Subjects'].str.replace('--', ';', regex=False)

    # 5. CREATE CATEGORIES (Local Mapping)
    print("  5. Creating Categories (Mapping)...")
    CATEGORY_MAPPINGS = {
        'sociologie': 'Sociology', 'sociology': 'Sociology',
        'sciences sociales': 'Social Science', 'social science': 'Social Science',
        'psychologie': 'Psychology', 'psychology': 'Psychology',
        'histoire': 'History', 'history': 'History',
        'éducation': 'Education', 'education': 'Education',
        'littérature': 'Literature', 'literature': 'Literature',
        'roman': 'Fiction', 'fiction': 'Fiction',
        'philosophie': 'Philosophy', 'philosophy': 'Philosophy',
        'politique': 'Politics', 'politics': 'Politics',
        'économie': 'Economics', 'economics': 'Economics',
        'droit': 'Law', 'law': 'Law',
        'science': 'Science', 'biologie': 'Biology', 'biology': 'Biology',
        'art': 'Art', 'arts': 'Art',
        'géographie': 'Geography', 'geography': 'Geography',
        'religion': 'Religion',
        'langue': 'Language', 'language': 'Language',
        'bande dessinée': 'Comics', 'comics': 'Comics',
        'biographie': 'Biography', 'biography': 'Biography'
    }

    def extract_categories(subjects_str):
        if pd.isna(subjects_str): return None
        categories = set()
        subjects_lower = subjects_str.lower()
        subjects_list = [s.strip() for s in subjects_str.split(';')]
        
        for key, category in CATEGORY_MAPPINGS.items():
            if key in subjects_lower:
                categories.add(category)
                if len(categories) >= 5: break
        
        if not categories:
            for subject in subjects_list[:5]:
                words = re.findall(r'\\b[A-Za-zÀ-ÿ]{5,}\\b', subject)
                if words:
                    categories.add(words[0].capitalize())
                    if len(categories) >= 5: break
        
        if categories:
            return '; '.join(sorted(list(categories))[:5])
        return None

    items_df['Category'] = items_df['Subjects'].apply(extract_categories)

    # 6. FIND MISSING CATEGORIES (API)
    print("  6. Finding Missing Categories (API)...")
    missing_cat_mask = items_df['Category'].isna()
    books_missing_cat = items_df[missing_cat_mask].copy()
    
    if len(books_missing_cat) > 0:
        print(f"     Searching for {len(books_missing_cat)} missing categories...")
        
        def get_categories_api(isbn, title, author):
            # Google Books
            try:
                query = f"isbn:{isbn}" if isbn else f"intitle:{title}"
                url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_API_KEY}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "items" in data:
                        cats = data["items"][0]["volumeInfo"].get("categories", [])
                        if cats: return '; '.join(cats[:5])
            except: pass
            
            time.sleep(0.2)
            
            # OpenLibrary
            try:
                if isbn:
                    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        key = f"ISBN:{isbn}"
                        if key in data:
                            subjects = data[key].get("subjects", [])
                            if subjects: return '; '.join([s['name'] for s in subjects[:5]])
            except: pass
            return None

        found_count = 0
        for idx, row in books_missing_cat.iterrows():
            isbn = row['ISBN Valid']
            title = row['Title']
            author = row['Author']
            
            cat = get_categories_api(isbn, title, author)
            if cat:
                items_df.at[idx, 'Category'] = cat
                found_count += 1
            time.sleep(0.4)
        print(f"     Found {found_count} new categories")

    # 7. FIND MISSING AUTHORS (API)
    print("  7. Finding Missing Authors (API)...")
    missing_auth_mask = items_df['Author'].isna()
    books_missing_auth = items_df[missing_auth_mask].copy()
    
    if len(books_missing_auth) > 0:
        print(f"     Searching for {len(books_missing_auth)} missing authors...")
        
        def get_author_api(isbn, title):
            # Google Books
            try:
                query = f"isbn:{isbn}" if isbn else f"intitle:{title}"
                url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_API_KEY}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "items" in data:
                        authors = data["items"][0]["volumeInfo"].get("authors", [])
                        if authors: return authors[0]
            except: pass
            
            time.sleep(0.2)
            
            # OpenLibrary
            try:
                if isbn:
                    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        key = f"ISBN:{isbn}"
                        if key in data:
                            authors = data[key].get("authors", [])
                            if authors: return authors[0].get("name")
            except: pass
            return None

        found_count = 0
        for idx, row in books_missing_auth.iterrows():
            isbn = row['ISBN Valid']
            title = row['Title']
            
            auth = get_author_api(isbn, title)
            if auth:
                items_df.at[idx, 'Author'] = auth
                found_count += 1
            time.sleep(0.4)
        print(f"     Found {found_count} new authors")

    # 8. FIND MISSING DATES (API) - Requested Feature
    print("  8. Finding Missing Dates (API)...")
    if 'Publication_Date' not in items_df.columns:
        items_df['Publication_Date'] = None
    
    missing_date_mask = items_df['Publication_Date'].isna()
    books_missing_date = items_df[missing_date_mask].copy()
    
    if len(books_missing_date) > 0:
        print(f"     Searching for {len(books_missing_date)} missing dates...")
        
        def get_date_api(isbn, title, author):
            # Google Books
            try:
                query = f"isbn:{isbn}" if isbn else f"intitle:{title}"
                if author: query += f" inauthor:{author}"
                url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_API_KEY}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "items" in data:
                        return data["items"][0]["volumeInfo"].get("publishedDate")
            except: pass
            
            time.sleep(0.2)
            
            # OpenLibrary
            try:
                if isbn:
                    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        key = f"ISBN:{isbn}"
                        if key in data:
                            return data[key].get("publish_date")
            except: pass
            return None

        found_count = 0
        for idx, row in books_missing_date.iterrows():
            isbn = row['ISBN Valid']
            title = row['Title']
            author = row['Author']
            
            date_str = get_date_api(isbn, title, author)
            if date_str:
                items_df.at[idx, 'Publication_Date'] = date_str
                found_count += 1
            time.sleep(0.4)
        print(f"     Found {found_count} new dates")

    # 9. EXTRACT YEARS (Final Parsing)
    print("  9. Extracting Years...")
    def extract_year(date_str):
        if pd.isna(date_str): return None
        date_str = str(date_str)
        year_match = re.search(r'\\b(19|20)\\d{2}\\b', date_str)
        if year_match:
            return int(year_match.group())
        return None

    items_df['Publication_Date'] = items_df['Publication_Date'].apply(extract_year)
    items_df['Publication_Date'] = items_df['Publication_Date'].astype('Int64')

    # 10. SAVE FINAL FILE
    print(f"  10. Saving to {ITEMS_ENRICHED_FILE}...")
    items_df.to_csv(ITEMS_ENRICHED_FILE, index=False)
    print("  ✓ Done.")

if __name__ == "__main__":
    process_interactions()
    enrich_items()
    print("\nALL ENRICHMENT STEPS COMPLETED SUCCESSFULLY")
