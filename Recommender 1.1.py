"""
Phase 11
============================================
Optimizes the hyperparameters of the Phase 5 (Advanced User-Based CF) model.
Parameters to tune:
1. Alpha (Recency Decay): [0.3, 0.5, 0.7, 1.0]
2. Sim Threshold: [0.01, 0.05, 0.1]
3. History Weight: [0.3, 0.5, 0.7, 0.9]

Target: Maximize MAP@10 
"""

import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from collections import defaultdict
import itertools
import time


# 1. DATA LOADING
print("\n[1/5] Loading data...")

interactions = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/original_df/interactions.csv')
interactions['date'] = pd.to_datetime(interactions['t'], unit='s')

# Mappings
users = sorted(interactions['u'].unique())
all_items = sorted(interactions['i'].unique())
user_map = {u: i for i, u in enumerate(users)}
item_map = {i: j for j, i in enumerate(all_items)}
idx_to_item = {j: i for i, j in item_map.items()}

n_users = len(users)
n_items = len(all_items)

print(f"✓ Interactions: {len(interactions):,}")

# 2. CORE FUNCTIONS
def build_matrices(interactions_df, alpha, sim_threshold):
    # Self-History (Recency)
    max_time = interactions_df['t'].max()
    rows, cols, data = [], [], []
    for _, row in interactions_df.iterrows():
        u = user_map[row['u']]
        i = item_map[row['i']]
        days_ago = (max_time - row['t']) / 86400
        score = 1.0 / ((days_ago + 1) ** alpha)
        rows.append(u)
        cols.append(i)
        data.append(score)
    S_self = csr_matrix((data, (rows, cols)), shape=(n_users, n_items))
    
    # User Similarity (Overlap)
    # Note: Similarity calculation doesn't depend on alpha, but threshold does filtering
    # To save time, we compute raw similarity ONCE and filter later?
    # No, let's just re-compute efficiently.
    
    data_bin = np.ones(len(rows))
    X_bin = csr_matrix((data_bin, (rows, cols)), shape=(n_users, n_items))
    Intersection = X_bin.dot(X_bin.T)
    user_counts = np.array(X_bin.sum(axis=1)).flatten()
    
    coo = Intersection.tocoo()
    rows_sim, cols_sim, data_sim = [], [], []
    for i, j, v in zip(coo.row, coo.col, coo.data):
        if i == j: continue
        union = user_counts[i] + user_counts[j] - v
        if union > 0:
            sim = v / union
            if sim > sim_threshold:
                rows_sim.append(i)
                cols_sim.append(j)
                data_sim.append(sim)
    Sim_User = csr_matrix((data_sim, (rows_sim, cols_sim)), shape=(n_users, n_users))
    
    return S_self, Sim_User

def evaluate_model(train_df, test_users, test_actual, alpha, sim_threshold, w_history):
    # Build Matrices
    S_self, Sim_User = build_matrices(train_df, alpha, sim_threshold)
    
    # Pre-compute Collab scores for efficiency?
    # No, do per-user to save memory
    
    aps = []
    
    # Optimization: Process in batches or just loop
    # For grid search speed, we'll use a subset of test users if needed, but let's try full
    
    for user in test_users:
        if user not in test_actual: continue
        u_idx = user_map[user]
        
        # History Score
        s_history = S_self[u_idx].toarray().flatten()
        
        # Collab Score
        user_sims = Sim_User[u_idx]
        s_collab = user_sims.dot(S_self).toarray().flatten()
        
        # Combine
        # w_history * History + (1-w_history) * Collab
        # Note: Collab scores are usually smaller (sum of sims < 1.0 often), while History is ~1.0
        # We might need to normalize, but let's stick to the simple weighted sum for now
        
        final_scores = s_history * w_history + s_collab * (1.0 - w_history)
        
        # Rank
        top_indices = np.argsort(final_scores)[::-1][:10]
        recs = [idx_to_item[idx] for idx in top_indices]
        
        # MAP
        actual = test_actual[user]
        hits = 0
        precision_sum = 0
        for rank, item in enumerate(recs[:len(actual)], 1): # Standard MAP@K usually checks top 10
             # Wait, MAP@10 checks top 10 regardless of actual size?
             # Kaggle metric: "Mean Average Precision @ 10"
             pass
             
        for rank, item in enumerate(recs, 1):
            if item in actual:
                hits += 1
                precision_sum += hits / rank
        
        aps.append(precision_sum / min(len(actual), 10))
        
    return np.mean(aps)

# 3. GRID SEARCH
print("\n[2/5] Preparing Grid Search...")

# Split Data
train_users, test_users = train_test_split(users, test_size=0.2, random_state=42)
train_users_set = set(train_users)

interactions_sorted = interactions.sort_values(['u', 't'])
train_indices = []
test_actual = defaultdict(set)

for user in users:
    user_ints = interactions_sorted[interactions_sorted['u'] == user]
    if user in train_users_set:
        train_indices.extend(user_ints.index)
    else:
        n = len(user_ints)
        split = int(n * 0.8)
        train_indices.extend(user_ints.index[:split])
        test_items = user_ints.iloc[split:]['i'].tolist()
        test_actual[user] = set(test_items)

train_df = interactions.loc[train_indices]

# Define Grid
alphas = [0.3, 0.5, 0.7, 1.0]
thresholds = [0.01, 0.05, 0.1]
weights = [0.3, 0.5, 0.7, 0.9]

best_score = -1
best_params = {}

print(f"  Testing {len(alphas) * len(thresholds) * len(weights)} combinations...")
print(f"  {'Alpha':<10} {'Thresh':<10} {'Weight':<10} {'MAP@10':<10} {'Time':<10}")
print("-" * 60)

# Loop
for alpha, thresh in itertools.product(alphas, thresholds):
    # Build matrices once per (alpha, thresh) pair
    start_build = time.time()
    S_self, Sim_User = build_matrices(train_df, alpha, thresh)
    build_time = time.time() - start_build
    
    # Pre-calculate Collab part to speed up weight tuning?
    # Actually, we can just run the eval loop for each weight
    
    for w in weights:
        start_eval = time.time()
        
        # Custom eval loop reusing matrices
        aps = []
        for user in test_users:
            if user not in test_actual: continue
            u_idx = user_map[user]
            
            s_history = S_self[u_idx].toarray().flatten()
            user_sims = Sim_User[u_idx]
            s_collab = user_sims.dot(S_self).toarray().flatten()
            
            final_scores = s_history * w + s_collab * (1.0 - w)
            
            top_indices = np.argsort(final_scores)[::-1][:10]
            recs = [idx_to_item[idx] for idx in top_indices]
            
            actual = test_actual[user]
            hits = 0
            precision_sum = 0
            for rank, item in enumerate(recs, 1):
                if item in actual:
                    hits += 1
                    precision_sum += hits / rank
            aps.append(precision_sum / min(len(actual), 10))
            
        score = np.mean(aps)
        eval_time = time.time() - start_eval
        
        print(f"  {alpha:<10} {thresh:<10} {w:<10} {score:.5f}      {eval_time:.1f}s")
        
        if score > best_score:
            best_score = score
            best_params = {'alpha': alpha, 'thresh': thresh, 'w': w}

print("\n" + "="*60)
print(f"BEST RESULT: MAP@10 = {best_score:.5f}")
print(f"Parameters: {best_params}")
print("="*60)

# 4. FINAL SUBMISSION

alpha = best_params['alpha']
thresh = best_params['thresh']
w = best_params['w']

S_self_full, Sim_User_full = build_matrices(interactions, alpha, thresh)

recommendations = []
for i, user in enumerate(users):
    u_idx = user_map[user]
    
    s_history = S_self_full[u_idx].toarray().flatten()
    user_sims = Sim_User_full[u_idx]
    s_collab = user_sims.dot(S_self_full).toarray().flatten()
    
    final_scores = s_history * w + s_collab * (1.0 - w)
    
    top_indices = np.argsort(final_scores)[::-1][:10]
    recs = [idx_to_item[idx] for idx in top_indices]
    
    # Fallback
    if len(recs) < 10:
        popular = interactions['i'].value_counts().index.tolist()
        for item in popular:
            if item not in recs:
                recs.append(item)
                if len(recs) >= 10: break
    
    rec_str = ' '.join(map(str, recs[:10]))
    recommendations.append({'user_id': user, 'recommendation': rec_str})
    
    if (i+1) % 1000 == 0:
        print(f"    Processed {i+1} users...")

sub_df = pd.DataFrame(recommendations)
sub_df.to_csv('submission.csv', index=False)
print("✓ Saved to submission.csv")
