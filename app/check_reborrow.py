import pandas as pd

# Load history
df = pd.read_csv('Books_Recommander_System-main/user_borrowing_history.csv')

total_borrows = 0
unique_borrows = 0

for ids_str in df['books_borrowed']:
    if pd.isna(ids_str): continue
    ids = [x.strip() for x in str(ids_str).split(',') if x.strip().isdigit()]
    total_borrows += len(ids)
    unique_borrows += len(set(ids))

reborrow_count = total_borrows - unique_borrows
reborrow_rate = (reborrow_count / total_borrows * 100) if total_borrows > 0 else 0

print(f"Total Borrows: {total_borrows}")
print(f"Unique Borrows: {unique_borrows}")
print(f"Reborrow Count: {reborrow_count}")
print(f"Reborrow Rate: {reborrow_rate:.2f}%")
