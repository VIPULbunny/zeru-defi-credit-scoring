# Zeru Finance: DeFi Credit Scoring Final Script
# Author: Vipul Solanki

import pandas as pd
import numpy as np
import json
import zipfile
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

# --- Step 1: Extract ZIP ---
zip_path = "D:/JOB and Internship/Internship/Zeru Task/user-wallet-transactions.zip"
extract_dir = "D:/JOB and Internship/Internship/Zeru Task"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# --- Step 2: Load JSON ---
file_path = os.path.join(extract_dir, "user-wallet-transactions.json")
with open(file_path, "r") as file:
    data = json.load(file)

df = pd.DataFrame(data)

# --- Step 3: Basic Cleaning ---
df = df.dropna(subset=['userWallet'])
df = df[df['actionData'].apply(lambda x: isinstance(x, dict) and 'amount' in x)]
valid_actions = ['deposit', 'borrow', 'repay', 'redeemunderlying', 'liquidationcall']
df = df[df['action'].isin(valid_actions)]
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
df = df.dropna(subset=['timestamp'])
df['amount'] = df['actionData'].apply(lambda x: float(x.get('amount', 0)))
df = df[df['amount'] >= 0]
df['asset'] = df['actionData'].apply(lambda x: x.get('asset', None))

# --- Step 4: Extract Fields from actionData ---
df['createdAt'] = pd.to_datetime(df['createdAt'].apply(lambda x: x.get('$date') if isinstance(x, dict) else None))
df['updatedAt'] = pd.to_datetime(df['updatedAt'].apply(lambda x: x.get('$date') if isinstance(x, dict) else None))
df['ts_date'] = df['timestamp'].dt.date
df['ts_hour'] = df['timestamp'].dt.hour
df['ts_dayofweek'] = df['timestamp'].dt.dayofweek
df['ts_month'] = df['timestamp'].dt.month

df['tx_type'] = df['actionData'].apply(lambda x: x.get('type') if isinstance(x, dict) else None)
df['assetSymbol'] = df['actionData'].apply(lambda x: x.get('assetSymbol') if isinstance(x, dict) else None)
df['assetPriceUSD'] = df['actionData'].apply(lambda x: float(x.get('assetPriceUSD', 0)) if isinstance(x, dict) else None)
df['poolId'] = df['actionData'].apply(lambda x: x.get('poolId') if isinstance(x, dict) else None)
df['userId'] = df['actionData'].apply(lambda x: x.get('userId') if isinstance(x, dict) else None)

df['created_date'] = df['createdAt'].dt.date
df['created_time'] = df['createdAt'].dt.time
df['updated_date'] = df['updatedAt'].dt.date
df['updated_time'] = df['updatedAt'].dt.time

# --- Step 5: Drop Unneeded Columns ---
columns_to_drop = ['_id', '__v', 'network', 'protocol', 'txHash', 'logId', 'actionData', 'createdAt', 'updatedAt']
df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

# --- Step 6: Time Gap Between Transactions ---
df = df.sort_values(by=['userWallet', 'timestamp'])
df['time_gap'] = df.groupby('userWallet')['timestamp'].diff().dt.total_seconds()

# --- Step 7: Add USD Value ---
df['amount_usd'] = df['amount'] * df['assetPriceUSD']


# --- Step 8: Aggregation per Wallet ---


wallet_df = df.groupby('userWallet').agg(
    total_tx_count=('action', 'count'),
    num_deposits=('action', lambda x: (x == 'deposit').sum()),
    num_borrows=('action', lambda x: (x == 'borrow').sum()),
    num_repays=('action', lambda x: (x == 'repay').sum()),
    num_redeems=('action', lambda x: (x == 'redeemunderlying').sum()),
    num_liquidations=('action', lambda x: (x == 'liquidationcall').sum()),
    total_amount_deposited=('amount', lambda x: x[df.loc[x.index, 'action'] == 'deposit'].sum()),
    total_amount_borrowed=('amount', lambda x: x[df.loc[x.index, 'action'] == 'borrow'].sum()),
    total_amount_repaid=('amount', lambda x: x[df.loc[x.index, 'action'] == 'repay'].sum()),
    total_usd_value=('amount_usd', 'sum'),
    avg_time_gap=('time_gap', 'mean'),
    num_unique_assets=('assetSymbol', pd.Series.nunique)
).reset_index()


wallet_df = wallet_df[wallet_df['total_tx_count'] > 2]


wallet_df['repay_borrow_ratio'] = wallet_df['total_amount_repaid'] / (wallet_df['total_amount_borrowed'] + 1e-6)
wallet_df['avg_time_gap'] = wallet_df['avg_time_gap'].fillna(0)
wallet_df.fillna(0, inplace=True)
wallet_df['log_total_usd'] = np.log1p(wallet_df['total_usd_value'])
wallet_df = wallet_df[wallet_df['total_tx_count'] > 2]  # Optional but recommended

# --- Step 9: Score Generation ---

features = [
    'num_deposits', 'num_borrows', 'num_repays',
    'repay_borrow_ratio', 'num_liquidations',
    'avg_time_gap', 'log_total_usd'
]

wallet_df[features] = wallet_df[features].fillna(0)

scaler = MinMaxScaler()
scaled_features = scaler.fit_transform(wallet_df[features])
scaled_df = pd.DataFrame(scaled_features, columns=features)

weights = {
    'num_deposits': 0.20,
    'num_borrows': 0.15,
    'num_repays': 0.20,
    'repay_borrow_ratio': 0.15,
    'num_liquidations': -0.10,
    'avg_time_gap': 0.10,
    'log_total_usd': 0.20
}

wallet_df['credit_score'] = (scaled_df * pd.Series(weights)).sum(axis=1) * 1000
wallet_df['credit_score'] = wallet_df['credit_score'].clip(0, 1000)

# --- Step 10: EDA and Visualization ---
plt.figure(figsize=(10, 5))
sns.histplot(wallet_df['credit_score'], bins=10, kde=True, color='skyblue')
plt.title('Distribution of Credit Scores (0–1000)')
plt.xlabel('Credit Score')
plt.ylabel('Number of Wallets')
plt.grid(True)
plt.tight_layout()
plt.show()

# Score buckets
bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
labels = ['0-100', '100-200', '200-300', '300-400', '400-500',
          '500-600', '600-700', '700-800', '800-900', '900-1000']
wallet_df['score_bucket'] = pd.cut(wallet_df['credit_score'], bins=bins, labels=labels, right=False)

plt.figure(figsize=(12, 5))
wallet_df['score_bucket'].value_counts().sort_index().plot(kind='bar', color='orange')
plt.title('Wallet Count per Credit Score Bucket')
plt.xlabel('Credit Score Bucket')
plt.ylabel('Wallet Count')
plt.grid(axis='y')
plt.tight_layout()
plt.show()

# Correlation heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(wallet_df.corr(numeric_only=True), annot=True, fmt='.2f', cmap='coolwarm')
plt.title('Correlation Matrix of Wallet Features')
plt.tight_layout()
plt.show()

# Save result
wallet_df.to_csv("wallet_scores.csv", index=False)
