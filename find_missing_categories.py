import pandas as pd
import requests
import time

# Load the enriched dataset
items_df = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv',
                       dtype={'ISBN Valid': str, 'Publication_Date': 'Int64'})

# Category mapping for common subjects
CATEGORY_MAPPINGS = {
    'fiction': 'Fiction', 'novel': 'Fiction', 'literature': 'Literature',
    'history': 'History', 'historical': 'History',
    'science': 'Science', 'technology': 'Technology',
    'biography': 'Biography', 'autobiography': 'Biography',
    'poetry': 'Poetry', 'drama': 'Drama', 'theater': 'Theater',
    'philosophy': 'Philosophy', 'religion': 'Religion',
    'psychology': 'Psychology', 'sociology': 'Sociology',
    'education': 'Education', 'teaching': 'Education',
    'art': 'Art', 'music': 'Music', 'architecture': 'Architecture',
    'business': 'Business', 'economics': 'Economics',
    'law': 'Law', 'political': 'Politics', 'politics': 'Politics',
    'medicine': 'Medicine', 'health': 'Health',
    'travel': 'Travel', 'geography': 'Geography',
    'cooking': 'Cooking', 'food': 'Cooking',
    'sports': 'Sports', 'games': 'Games',
    'comics': 'Comics', 'graphic': 'Comics',
    'children': 'Children', 'juvenile': 'Children',
    'mathematics': 'Mathematics', 'physics': 'Physics',
    'chemistry': 'Chemistry', 'biology': 'Biology',
}

def get_categories_from_google_books(isbn=None, title=None, author=None):
    """Get categories from Google Books API"""
    try:
        if isbn:
            query = f"isbn:{isbn}"
        elif title:
            query = f"intitle:{title}"
            if author:
                query += f" inauthor:{author}"
        else:
            return None
        
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": query, "maxResults": 1}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                volume_info = data['items'][0].get('volumeInfo', {})
                categories = volume_info.get('categories', [])
                if categories:
                    return categories
        
        return None
    except:
        return None

def get_categories_from_openlibrary(isbn=None, title=None, author=None):
    """Get categories from OpenLibrary API"""
    try:
        if isbn:
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                book_key = f"ISBN:{isbn}"
                if book_key in data:
                    subjects = data[book_key].get('subjects', [])
                    if subjects:
                        return [s['name'] for s in subjects[:5]]
        else:
            # Search by title/author
            url = "https://openlibrary.org/search.json"
            params = {'title': title, 'author': author, 'limit': 1}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('docs') and len(data['docs']) > 0:
                    subjects = data['docs'][0].get('subject', [])
                    if subjects:
                        return subjects[:5]
        
        return None
    except:
        return None

def extract_categories_from_subjects(subjects_list):
    """Extract 1-5 category keywords from API subjects"""
    if not subjects_list:
        return None
    
    categories = set()
    
    for subject in subjects_list:
        subject_lower = subject.lower()
        
        # Try to match known categories
        for key, category in CATEGORY_MAPPINGS.items():
            if key in subject_lower:
                categories.add(category)
                if len(categories) >= 5:
                    break
        
        # If no match, use first meaningful word
        if len(categories) < 5:
            words = subject.split()
            if words:
                categories.add(words[0].capitalize())
        
        if len(categories) >= 5:
            break
    
    if categories:
        return '; '.join(sorted(list(categories))[:5])
    
    return None

# Filter books with no category
missing_category = items_df['Category'].isna()
books_to_process = items_df[missing_category].copy()

print(f"Searching categories for {len(books_to_process)} books...")
print("This will take approximately {:.1f} minutes with rate limiting.\n".format(len(books_to_process) * 0.4 / 60))

found_count = 0
not_found_count = 0

for idx, row in books_to_process.iterrows():
    isbn = row['ISBN Valid'] if pd.notna(row['ISBN Valid']) else None
    title = row['Title'] if pd.notna(row['Title']) else None
    author = row['Author'] if pd.notna(row['Author']) else None
    
    # Try Google Books first
    subjects = get_categories_from_google_books(isbn, title, author)
    source = "Google Books"
    
    if not subjects:
        time.sleep(0.2)
        # Try OpenLibrary
        subjects = get_categories_from_openlibrary(isbn, title, author)
        source = "OpenLibrary"
    
    if subjects:
        category = extract_categories_from_subjects(subjects)
        if category:
            items_df.at[idx, 'Category'] = category
            found_count += 1
            if found_count % 50 == 0:
                print(f"Progress: {found_count + not_found_count}/{len(books_to_process)} - Found {found_count} categories")
        else:
            not_found_count += 1
    else:
        not_found_count += 1
    
    time.sleep(0.4)  # Rate limiting

# Save updated dataset
items_df.to_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv', index=False)

# Final statistics
final_missing = items_df['Category'].isna().sum()
total = len(items_df)

print(f"\n{'='*80}")
print("CATEGORY ENRICHMENT COMPLETE")
print(f"{'='*80}")
print(f"Categories found via API: {found_count}")
print(f"Not found: {not_found_count}")
print(f"\nFinal statistics:")
print(f"Books WITH category: {total - final_missing}/{total} ({(total-final_missing)/total*100:.2f}%)")
print(f"Books with NO category: {final_missing}/{total} ({final_missing/total*100:.2f}%)")
print(f"\n✓ Updated items_enriched.csv")
