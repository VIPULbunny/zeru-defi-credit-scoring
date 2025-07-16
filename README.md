# README.md

## Zeru Finance - DeFi Credit Scoring

### Author: Vipul Solanki

### Submission for: Internship Assignment - Credit Scoring from Wallet Activity

---

## Problem Statement

Given transaction-level JSON data from Aave V2 protocol on Polygon, assign a **credit score (0–1000)** to each wallet address based on its behavioral activity like deposit, borrow, repay, liquidation, etc.

## Dataset

* Raw File: `user-wallet-transactions.json`
* Format: List of dictionaries (JSON array)
* Size: \~87MB (uncompressed)

Each entry in the dataset contains fields like:

* Wallet Address (`userWallet`)
* Action (`deposit`, `borrow`, `repay`, etc.)
* Timestamps
* Asset amount & price
* Pool, asset symbols, and user metadata

---

## Project Structure

```
.
zeru-defi-credit-scoring/
│
├── zeru_credit_scoring.py
├── wallet_scores.csv
├── README.md
├── analysis.md
├── histogram_credit_score.png
├── correlation_matrix.png
├── score_bucket_distribution.png

```

---

## Methodology

### 1. Data Cleaning

* Removed records with missing `userWallet`, malformed `actionData`, or invalid timestamps.
* Filtered only valid Aave V2 actions:

  * `deposit`, `borrow`, `repay`, `redeemunderlying`, `liquidationcall`
* Converted timestamps to datetime and extracted:

  * Hour, day, month
* Extracted `amount`, `asset`, `assetSymbol`, `assetPriceUSD`, etc.

### 2. Feature Engineering

* Computed `amount_usd = amount * assetPriceUSD`
* Calculated per-wallet aggregates:

  * Number of deposits, borrows, repays
  * Amount deposited, borrowed, repaid
  * Average time gap between transactions
  * Repay-to-borrow ratio
  * Count of unique asset symbols used

### 3. Credit Score Model

**Features selected:**

* `num_deposits`, `num_borrows`, `num_repays`, `repay_borrow_ratio`
* `num_liquidations`, `avg_time_gap`, `total_usd_value`

**Weights:**

```python
weights = {
  'num_deposits': 0.15,
  'num_borrows': 0.10,
  'num_repays': 0.20,
  'repay_borrow_ratio': 0.20,
  'num_liquidations': -0.20,
  'avg_time_gap': 0.10,
  'total_usd_value': 0.25
}
```

* Features normalized using MinMaxScaler (0–1 scale)
* Weighted sum scaled to **0–1000** using:
  `credit_score = sum(weights * scaled_features) * 1000`
* Clipped to stay within \[0, 1000]

---

## Result

* Credit scores generated for each wallet
* Distribution analysis provided in `analysis.md`

---

## How to Run

```bash
python zeru_credit_scoring.py
```

Ensure the extracted `user-wallet-transactions.json` file is in the same directory.

---

## License

Open for educational use only.

## Contact

* [LinkedIn](https://www.linkedin.com/in/vipulsolanki777/)
* [GitHub](https://github.com/VIPULbunny)
* Email: [vipulsolanki339@gmail.com](mailto:vipulsolanki339@gmail.com)
