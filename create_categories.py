import pandas as pd
import re

# Load the enriched dataset with proper dtypes
items_df = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv',
                       dtype={'Publication_Date': 'Int64', 'ISBN Valid': str})

# Common category mappings (French to English categories)
CATEGORY_MAPPINGS = {
    # Social Sciences
    'sociologie': 'Sociology',
    'sociology': 'Sociology',
    'sciences sociales': 'Social Science',
    'social science': 'Social Science',
    'psychologie': 'Psychology',
    'psychology': 'Psychology',
    'anthropologie': 'Anthropology',
    'anthropology': 'Anthropology',
    
    # History
    'histoire': 'History',
    'history': 'History',
    'historique': 'History',
    
    # Education
    'éducation': 'Education',
    'education': 'Education',
    'enseignement': 'Education',
    'teaching': 'Education',
    'pédagogie': 'Education',
    
    # Literature
    'littérature': 'Literature',
    'literature': 'Literature',
    'roman': 'Fiction',
    'fiction': 'Fiction',
    'poésie': 'Poetry',
    'poetry': 'Poetry',
    
    # Philosophy
    'philosophie': 'Philosophy',
    'philosophy': 'Philosophy',
    
    # Politics
    'politique': 'Politics',
    'politics': 'Politics',
    
    # Economics
    'économie': 'Economics',
    'economics': 'Economics',
    
    # Law
    'droit': 'Law',
    'law': 'Law',
    'juridique': 'Law',
    
    # Science
    'science': 'Science',
    'biologie': 'Biology',
    'biology': 'Biology',
    'physique': 'Physics',
    'physics': 'Physics',
    'chimie': 'Chemistry',
    'chemistry': 'Chemistry',
    
    # Arts
    'art': 'Art',
    'arts': 'Art',
    'musique': 'Music',
    'music': 'Music',
    'théâtre': 'Theater',
    'theater': 'Theater',
    
    # Geography
    'géographie': 'Geography',
    'geography': 'Geography',
    
    # Religion
    'religion': 'Religion',
    'théologie': 'Theology',
    'theology': 'Theology',
    
    # Language
    'langue': 'Language',
    'language': 'Language',
    'linguistique': 'Linguistics',
    'linguistics': 'Linguistics',
    
    # Comics
    'bande dessinée': 'Comics',
    'bandes dessinées': 'Comics',
    'comics': 'Comics',
    
    # Biography
    'biographie': 'Biography',
    'biography': 'Biography',
    'autobiographie': 'Biography',
}

def extract_categories(subjects_str):
    """Extract 1-5 category keywords from subjects string"""
    if pd.isna(subjects_str):
        return None
    
    categories = set()
    subjects_lower = subjects_str.lower()
    
    # Split by semicolons and process each subject
    subjects_list = [s.strip() for s in subjects_str.split(';')]
    
    # Try to match known categories
    for key, category in CATEGORY_MAPPINGS.items():
        if key in subjects_lower:
            categories.add(category)
            if len(categories) >= 5:
                break
    
    # If no matches, extract key words from subjects
    if not categories:
        for subject in subjects_list[:5]:  # Look at first 5 subjects
            # Clean and extract meaningful words (longer than 4 chars)
            words = re.findall(r'\b[A-Za-zÀ-ÿ]{5,}\b', subject)
            if words:
                # Capitalize first word as category
                categories.add(words[0].capitalize())
                if len(categories) >= 5:
                    break
    
    # Return semicolon-separated categories (1-5)
    if categories:
        return '; '.join(sorted(list(categories))[:5])
    
    return None

# Create Category column
print("Extracting categories from Subjects column...")
items_df['Category'] = items_df['Subjects'].apply(extract_categories)

# Statistics
total = len(items_df)
with_category = items_df['Category'].notna().sum()
missing = total - with_category

print(f"\n✓ Successfully created Category column")
print(f"Books with categories: {with_category}/{total} ({with_category/total*100:.2f}%)")
print(f"Missing categories: {missing}/{total} ({missing/total*100:.2f}%)")

# Save back to the same file
items_df.to_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv', index=False)
print("\n✓ Updated items_enriched.csv with Category column")

# Show samples
print("\nSample results (Subjects → Category):")
print("=" * 120)
sample_df = items_df[items_df['Category'].notna()][['Subjects', 'Category']].head(10)
for idx, row in sample_df.iterrows():
    subjects = row['Subjects'][:80] + '...' if len(str(row['Subjects'])) > 80 else row['Subjects']
    print(f"\nSubjects: {subjects}")
    print(f"Category: {row['Category']}")
