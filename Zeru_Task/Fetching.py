import pandas as pd
import requests

# Constants
API_KEY = "cqt_rQDycJfCyx73kXwgBdDtbtxcr3xh"
CHAIN_ID = "1"  # Ethereum Mainnet
CSV_PATH = r"D:\JOB and Internship\Internship\Zeru Task\Zeru_Task\wallet_id.csv"

# Load wallet IDs
df_wallets = pd.read_csv(CSV_PATH)
wallet_ids = df_wallets['wallet_id'].tolist()

# Function to fetch transaction data for a wallet
def fetch_transactions(wallet_id):
    url = f"https://api.covalenthq.com/v1/{CHAIN_ID}/address/{wallet_id}/transactions_v3/"
    response = requests.get(url, params={"key": API_KEY})
    if response.status_code != 200:
        print(f"[ERROR] {wallet_id} → Status: {response.status_code}")
        return []
    data = response.json()
    return data.get("data", {}).get("items", [])

# Fetch and print data for first 5 wallets
for i, wallet in enumerate(wallet_ids[:1]):
    print(f"\n=== Wallet {i+1}: {wallet} ===")
    tx_data = fetch_transactions(wallet)
    if not tx_data:
        print("No transactions found or failed to fetch.")
    else:
        print(f"Total Transactions Fetched: {len(tx_data)}")
        print("Sample Transaction:")
        print(tx_data[0])  # print first transaction as sample
