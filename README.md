# Books_Recommander_System

Database and code made in the context of a Kaggle competition where we aimed to get the best @MAP10 score.

In other words, the goal is to code a suggestion algorithm that is the most accurate possible based on data of the books (15109 books) and the interaction matrix (user/item matrix).

To get it better i strongly suggest you read the readme ⬇⬇⬇⬇

## About the data cleaning and the making of items_enriched.csv

Executive Summary
This document details the complete data cleaning and enrichment pipeline applied to a book recommendation dataset. The process transformed a sparse, incomplete dataset into a rich, feature-complete resource suitable for building recommendation systems.

Key Achievements
96.04% ISBN coverage (up from 93.97%)
96.19% Author coverage (up from 82.58%)
95.66% Publication Date coverage (up from 0%)
91.10% Category coverage (up from 0%)

Total API Calls: ~18,000

📁 Dataset Overview
Original Dataset
Source: items.csv (15,291 books)
Interactions: interactions.csv (87,047 user-book interactions)

Final Enriched Dataset
Output: items_enriched.csv (15,109 books)
Filter Applied: Removed 182 books with zero interactions
Rationale: Focus on books with actual user engagement

Enrichment Strategy
Why Start with ISBN?
ISBN (International Standard Book Number) was prioritized as the primary enrichment target for strategic reasons:

Foundation for Other Enrichments

ISBNs are unique book identifiers
APIs (Google Books, OpenLibrary) provide most accurate results when queried by ISBN
Once ISBN is available, other metadata (author, date, category) is easier to obtain

ISBN-based API queries: ~95% success rate
Title-based API queries: ~40-60% success rate
Enriching ISBN first maximizes success for subsequent enrichments

ISBN ensures exact book matching (no ambiguity)
Prevents false matches from similar titles
Result: This ISBN-first approach enabled superior enrichment quality for all subsequent columns.

API Enrichment Strategy
All enrichments followed a cascading fallback strategy to maximize data recovery:

Cascading API Call Pattern
1st Attempt: Search by ISBN in Google Books API
    ↓ (if not found)
2nd Attempt: Search by ISBN in OpenLibrary API
    ↓ (if still not found OR no ISBN available)
3rd Attempt: Search by Title + Author in Google Books API
    ↓ (if not found)
4th Attempt: Search by Title + Author in OpenLibrary API
    ↓ (if still not found)
Result: Mark as "Not Found"

Primary source, better for recent publications
Returns: ISBN-13, authors, publication date, categories, subjects
Rate limit: 0.3s delay between requests
Success rate: ~95% for ISBN queries, ~60% for title queries
OpenLibrary API

Fallback source, better for older/rare books
Returns: ISBN, author names, first publish year, subjects
Rate limit: 0.4s delay between requests
Success rate: ~85% for ISBN queries, ~40% for title queries

## Complete Enrichment Pipeline
### Step 1: Data Import & Filtering
Purpose: Load data and filter relevant books

Actions:
Loaded items.csv (15,291 books)
Loaded interactions.csv (87,047 interactions)

Identified borrowed books (books with ≥1 interaction)
Filtered dataset to borrowed books only

Result:
Before: 15,291 books
After: 15,109 books
Removed: 182 unborrowed books (1.19%)


### Step 2: ISBN Cleaning
Purpose: Standardize ISBN format

Problem: Mixed ISBN formats

Multiple ISBNs per entry: 9782871303336; 2871303339
ISBN-10 and ISBN-13 mixed
Inconsistent separators and formatting

Solution:
Split multiple ISBNs by semicolon
Extract digits only
Keep first 13-digit ISBN starting with 978 or 979
Discard all other formats

Result:
Before: 14,369 books with ISBN (93.97%)
After: 14,367 books with clean ISBN (95.09%)
Missing: 742 books (4.91%)
Example:

Before: "9782871303336; 2871303339"
After:  "9782871303336"

### Step 3: ISBN Finding via APIs
Purpose: Find ISBNs for 742 books missing them

Strategy:
Query Google Books API by Title + Author
Fallback to OpenLibrary API if not found
Extract ISBN-13 from results

Result:
ISBNs Found: 146
Still Missing: 596
Success Rate: 19.7%

Impact:
Total with ISBN: 14,511 books (96.04%)
Final Missing: 598 books (3.96%)

### Step 4: Publication Date Enrichment
Purpose: Add publication year for all books

Strategy (Cascading):

For books WITH ISBN: Query by ISBN (most accurate)
For books WITHOUT ISBN: Query by Title + Author
Google Books first, OpenLibrary fallback
Process:

Queried all 15,109 books

~18,000 API calls made

Result:
Dates Found: 14,828 (98.14%)
Missing: 281 (1.86%)
Date Format Handling:

Received mixed formats: "2019-01-15", "Nov 09, 2011", "2020"
Extraction: Regex pattern \b(19|20)\d{2}\b to extract 4-digit year
Output: Clean integer years (2011, 2020, etc.)
Final Publication_Date Column:

Coverage: 14,453 books with years (95.66%)
Format: Integer year only (no decimals, no dates)

### Step 5: Subject Cleaning
Purpose: Standardize subject separators

Problem: Inconsistent separators

Used: Histoire--Sciences sociales--Méthodologie
Standard: semicolons preferred

Solution:
Replace all "--" with ";"

Result:
Before: "Histoire--Sciences sociales--Méthodologie"
After:  "Histoire; Sciences sociales; Méthodologie"
Standardized: All subject separators
Impact: Easier parsing for category extraction

### Step 6: Category Creation
Purpose: Create high-level categories from detailed subjects

Strategy:
Parse subjects (semicolon-separated)
Map keywords to standardized categories
Extract 1-5 main categories per book
Category Mappings: 50+ mappings including:

French → English: "sociologie" → "Sociology"
Subject variations: "histoire", "history", "historique" → "History"
Common categories: Fiction, Science, Education, Literature, etc.

Extraction Logic:
Check each subject term against mapping dictionary
Add matched category (max 5 per book)
If no matches, extract meaningful keywords (5+ chars)
Return semicolon-separated category list

Result:
Initial Coverage: 12,913 books (85.47%)
Missing: 2,196 books (14.53%)

Example:
Subjects:  "Histoires de vie en sociologie; Sciences sociales; Méthodologie"
Category:  "History; Science; Social Science; Sociology"

### Step 7: Category Enrichment via APIs
Purpose: Find categories for 2,196 books without them

Strategy (Cascading):
Query Google Books API (by ISBN or Title+Author)
Extract 
categories or subjects fields
Fallback to OpenLibrary API
Map extracted subjects to standardized categories
Process:

Queried 2,196 books
Rate limiting: 0.4s delay
Total time: ~2 hours

Result:
Categories Found: 852
Still Missing: 1,344
Success Rate: 38.8%
Final Category Column:

Total Coverage: 13,765 books (91.10%)
Missing: 1,344 books (8.90%)
Format: Semicolon-separated keywords
Step 8: Author Enrichment via APIs
Purpose: Find authors for books missing them

Initial State:
Missing Authors: 2,632 books (17.42%)
Strategy (Cascading):

Query Google Books API (by ISBN or Title)
Extract authors field
Fallback to OpenLibrary API
Join multiple authors with commas (max 3)

Process:
Queried 2,632 books
Rate limiting: 0.4s delay
Total time: ~18 minutes

Result:
Authors Found: 2,057
Still Missing: 575
Success Rate: 78.2%
Final Author Column:

Total Coverage: 14,534 books (96.19%)
Missing: 575 books (3.81%)
Improvement: +13.61 percentage points

## 📊 Final Dataset Statistics

<img width="615" height="439" alt="Capture d’écran 2025-12-07 à 14 24 40" src="https://github.com/user-attachments/assets/c8e27383-e400-4987-9be9-c4854d00791d" />

### Missing Data Breakdown
<img width="604" height="319" alt="Capture d’écran 2025-12-07 à 14 25 40" src="https://github.com/user-attachments/assets/2559f3a1-cb70-4d64-a11a-a0b0c8d97206" />

### API Usage Summary
<img width="611" height="310" alt="Capture d’écran 2025-12-07 à 14 26 41" src="https://github.com/user-attachments/assets/6452e424-34ea-4479-bcda-12c681602ea2" />

## 🎯 Why Remaining Data is Missing
Books Still Missing Data
ISBN (598 books - 3.96%):

Very old publications (pre-ISBN era)
Self-published works
Internal/institutional publications
Non-standard publications (theses, reports)
Author (575 books - 3.81%):

Anonymous works
Corporate/institutional authors
Reference materials without attributed authors
Government publications
Publication Date (656 books - 4.34%):

Undated materials
Works with unknown publication info
Not indexed in major APIs
Category (1,344 books - 8.90%):

Highly specialized/niche topics
No subject metadata in APIs
Books without standardized categorization


## Using the Enriched Dataset
File Structure
Kaggle_datas/
-> items_enriched.csv          # ← USE THIS (enriched dataset)
-> interactions.csv            # User-book interactions
-> all_in_one_enrichment.py   # Enrichment pipeline (reference)

I first did the enrichment / Cleanning with each part in a different files so i can rerun only one part of the all process (to avoid running again an API call of 18 000 calls (Which can last ≈8 hours 😅) 
But in order to make it simple and clear in this repository i merged them all in the "all_in_one_enrichement.py" file so if you want to try the recommender system from the real original dataset "items.csv" and loose ≈20h to 35h instead of using the already clean/enriched version of the data base named "items_enriched.csv" you can...

### The variables dictionnary 
- For items_enriched
Category - Genre (91.10% coverage)
Author - Book author (96.19% coverage)
Publication_Date - Year published (95.66% coverage)
Subjects - Detailed topics (85.47% coverage)
ISBN Valid - Unique identifier (96.04% coverage)

- For interactions.csv
 - 87,047 user-book interactions
User ID (u), Item ID (i)



## Limitation of data cleaning

Title-based queries may return incorrect matches (~5% error rate)
Manually verified random sample: 95% accuracy
Language Bias

Better results for English/French books
Some non-Latin script books have lower coverage
References

APIs Used:
Google Books API
OpenLibrary API

Data Source:
Original dataset from Kaggle book recommendation competition

Tools:
Python 3.x
pandas, requests libraries
Rate limiting: 0.3-0.4s delays

## Contact & Acknowledgments
This enrichment pipeline was developed for a Kaggle book recommendation competition. The approach prioritizes data quality and demonstrates best practices in API-based data enrichment.

### Key Principles Applied:
- ISBN-first enrichment strategy
- Cascading API fallbacks
- Quality over speed
- Reproducible pipeline
- Production-ready output
  
Result: A clean, feature-rich dataset suitable for building high-quality recommendation systems.


## For the "interactions.csv" file
We have changed the time format to an understandable one
Then create to new file: 
- "user_borrowing_history.csv" that gives us all the books borrowed by each user and the date of every of the interaction
- "book_user_history.csv" that give for every books all the user that borrowed them and the date of the interactions as well

# The Recommender System

Important points:
- A user is more likely to borrow again a book that he already borrowed
- If a user A borrow the book 1 and the user B also borrowed the book 1, then if the the user A borrow the book 2, the user B is likely to borrow the book 2 also (User-User similarity)
- A book borrowed long ago should have less wheight on the recommendation than a book recently borrowed
- If a book 1 is borrowed by a User A, and a book 2 is very similar to the book 1 then the user A is more likely to borrow it also (Item-Item similarity)


We found that 26.47% of all interactions are re-borrows. Whiche is very important as some model systematicly exclude already borrowed books thinking Users would like new books. But it's not the case. 

## Our best recommender at the moment:

### The 3 Knobs We Tuned
We tested 48 different combinations of these three parameters:

#### 1. Recency Decay ($\alpha$)
What it does: Controls how fast a book's value drops over time.
Formula: $Score = \frac{1}{(days_ago + 1)^\alpha}$
The Test: We tried 0.3 (Slow decay), 0.5 (Medium), 0.7 (Fast), 1.0 (Very Fast).
The Winner: 0.7.
Meaning: Users in this dataset care a lot about what they read very recently. A book read yesterday is worth much more than one read last week.
#### 2. Similarity Threshold
What it does: Controls who qualifies as your "Neighbor".
The Test: We tried 0.01 (Loose), 0.05 (Standard), 0.1 (Strict).
The Winner: 0.05.
Meaning: We need a balance. If we are too strict (0.1), we find no neighbors. If too loose (0.01), we get noisy neighbors. 5% overlap is the "Goldilocks" zone.
#### 3. History Weight ($w$)
What it does: Controls the balance between Habit (Your History) and Discovery (Neighbors' History).
Formula: $Final = w \cdot History + (1-w) \cdot Discovery$
The Test: We tried 0.3 (Trust Neighbors), 0.5 (Balanced), 0.7 (Trust Self), 0.9 (Trust Self Heavily).
The Winner: 0.9.
Meaning: This is the most critical finding. 90% of the signal comes from your own history. The "Social" signal is useful, but only as a 10% "spice" on top of the strong "Habit" main course.
The Final Mathematical Model

With these optimal parameters, the final scoring function is:
$$Score(u, i) = 0.9\cdot\underbrace{\left(\sum\frac{1}{(t+1)^{0.7}}\right)}{\text{Your Habit}} + 0.1\cdot\underbrace{\left(\sum{v\in Neighbors} Sim(u,v)\cdot Score_v(i)\right)}_{\text{Social Discovery}}$$






Last Updated: December 2025
