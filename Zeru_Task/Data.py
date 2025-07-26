import requests
import pandas as pd
import time

API_KEY = "cqt_rQDycJfCyx73kXwgBdDtbtxcr3xh"
CHAIN_ID = 1  # Ethereum Mainnet
PROTOCOL = "compound"  # Use lowercase
SLEEP_INTERVAL = 1.1  # To avoid rate-limiting

def fetch_wallet_data(wallet_address):
    url = f"https://api.covalenthq.com/v1/{CHAIN_ID}/address/{wallet_address}/stacks/{PROTOCOL}/v2/"
    params = {
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"❌ Failed for {wallet_address} with status {response.status_code}")
        return None
    
    data = response.json().get("data", {})
    items = data.get("items", [])
    
    # If no protocol interaction, return zeros
    if not items:
        return {
            "borrow_count": 0,
            "repay_count": 0,
            "borrow_amount": 0.0,
            "repay_amount": 0.0,
            "liquidations": 0,
            "collateral": 0.0
        }

    borrow_count = 0
    repay_count = 0
    borrow_amount = 0.0
    repay_amount = 0.0
    liquidations = 0
    collateral = 0.0

    for item in items:
        borrow_count += item.get("borrow_count", 0)
        repay_count += item.get("repay_count", 0)
        borrow_amount += item.get("total_borrowed_quote", 0.0)
        repay_amount += item.get("total_repaid_quote", 0.0)
        liquidations += item.get("liquidation_count", 0)
        collateral += item.get("total_collateral_quote", 0.0)

    return {
        "borrow_count": borrow_count,
        "repay_count": repay_count,
        "borrow_amount": borrow_amount,
        "repay_amount": repay_amount,
        "liquidations": liquidations,
        "collateral": collateral
    }

def compute_credit_score(features):
    # Basic scoring formula (range: 0–1000)
    score = 500
    score += features["repay_count"] * 10
    score -= features["borrow_count"] * 5
    score -= features["liquidations"] * 50
    score += features["collateral"] * 0.05  # e.g., $1000 = +50

    score = max(0, min(1000, int(score)))
    return score

def main():
    df = pd.read_csv("wallets.csv")  # Make sure this file exists in the same folder
    results = []

    for i, row in df.iterrows():
        wallet = row["wallet_id"]
        print(f"\n🔄 Processing Wallet {i + 1}/{len(df)}: {wallet}")

        features = fetch_wallet_data(wallet)

        if features is None:
            # On 404 or error
            features = {
                "borrow_count": 0,
                "repay_count": 0,
                "borrow_amount": 0.0,
                "repay_amount": 0.0,
                "liquidations": 0,
                "collateral": 0.0
            }

        credit_score = compute_credit_score(features)
        features["wallet_id"] = wallet
        features["credit_score"] = credit_score
        print(f"✅ Features: {features}")

        results.append(features)
        time.sleep(SLEEP_INTERVAL)

    output_df = pd.DataFrame(results)
    output_df.to_csv("wallet_scores.csv", index=False)
    print("\n🎉 All done! Output saved to wallet_scores.csv")

if __name__ == "__main__":
    main()
