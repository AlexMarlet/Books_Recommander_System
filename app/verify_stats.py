import pandas as pd
from src.statistics import calculate_global_stats, calculate_user_stats, prepare_cluster_data

# Load Data
print("Loading data...")
history = pd.read_csv('Books_Recommander_System-main/user_borrowing_history.csv')
items = pd.read_csv('Books_Recommander_System-main/items_enriched.csv')
submissions = pd.read_csv('submission.csv')

# 1. Test Global Stats
print("\nTesting Global Stats...")
g_stats = calculate_global_stats(history, items, submissions)
print(f"Reborrow Rate: {g_stats['Reborrow Rate']:.2f}% (Expected ~26.47%)")
assert abs(g_stats['Reborrow Rate'] - 26.47) < 0.1, "Reborrow Rate Mismatch!"

# 2. Test Cluster Data
print("\nTesting Cluster Data...")
cluster_data = prepare_cluster_data(items)
print(f"Cluster Data Rows: {len(cluster_data)}")
assert 'x' in cluster_data.columns and 'y' in cluster_data.columns, "Missing Coordinates!"
assert 'Main_Category' in cluster_data.columns, "Missing Main_Category!"
assert 'Category_Grouped' in cluster_data.columns, "Missing Category_Grouped!"

unique_cats = cluster_data['Category_Grouped'].nunique()
print(f"Unique Grouped Categories: {unique_cats}")
assert unique_cats <= 20, f"Too many categories! Found {unique_cats}"

# 3. Test User Stats
print("\nTesting User Stats...")
u_stats = calculate_user_stats(history)
print(f"User Stats Rows: {len(u_stats)}")
print(u_stats.head())

print("\nALL TESTS PASSED!")
