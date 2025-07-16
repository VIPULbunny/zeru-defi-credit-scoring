# 📊 Wallet Score Analysis (Zeru Finance Credit Scoring)

## 🔍 Summary

This report summarizes the credit scoring of DeFi wallets using Aave V2 transaction history. A custom scoring algorithm (0–1000) was used to rank wallets by reliability, based on transactional behavior such as deposits, borrows, repayments, and liquidations.

---

## 📋 Dataset Overview

- **Total Wallet Records Analyzed**: ~`100,000` transactions  
- **Unique Wallets Scored**: `≈ 3,400+`
- **Final Aggregated Dataset Shape**: `3,400 rows × 14 columns`

### Final Columns Used:

- `userWallet`
- `total_tx_count`
- `num_deposits`, `num_borrows`, `num_repays`, `num_redeems`, `num_liquidations`
- `total_amount_deposited`, `total_amount_borrowed`, `total_amount_repaid`
- `total_usd_value`
- `repay_borrow_ratio`
- `avg_time_gap`
- `credit_score`

---

## 🧼 Null Value Analysis

| Column               | Null Count | % Null    |
|----------------------|------------|-----------|
| `avg_time_gap`       | 44         | 1.29%     |
| `repay_borrow_ratio` | 0          | 0.00%     |
| `total_usd_value`    | 0          | 0.00%     |
| `credit_score`       | 0          | 0.00%     |

> Nulls in `avg_time_gap` occur when a wallet has only one transaction. These are imputed as 0.

---

## 📈 Score Distribution

### Histogram

A large portion of wallets fall between **100–300**, indicating low or moderate DeFi activity.

![Credit Score Histogram](https://github.com/user-attachments/assets/97264889-cc12-4c6e-a01c-7b923d54cb24)

---

### Score Buckets (0–1000)

0-100    ████████

100-200  ███████████████

200-300  ███████████████

300-400  ██████

400-500  █████

500-600  ███

600-700  ██

700-800  █

800-900  █

900-1000 █

---

## 📊 Correlation Matrix

Visual representation of correlation between wallet behaviors and credit score:

![Correlation Matrix](https://github.com/user-attachments/assets/80a11692-9918-4654-a39f-19c26643650b)

### 🔗 Observations:

- `total_usd_value` and `repay_borrow_ratio` strongly influence credit score
- `num_liquidations` shows negative correlation with both score and responsible behaviors
- `avg_time_gap` is mildly correlated — longer gaps often suggest thoughtful activity

---

## 🧪 Feature Dependencies

- **`repay_borrow_ratio`** = Total repaid / Total borrowed → Critical for score
- **`avg_time_gap`** = Time difference between transactions → Reflects user strategy
- **`total_usd_value`** = Transaction impact → Higher values suggest committed users
- **`num_liquidations`** = Key negative signal → Indicates over-leveraged or failed positions

---

## 🧠 Behavior by Score Bucket

### 🟥 Wallets in 0–100
- Frequent `liquidationcall` actions
- Poor repayment ratio
- Tiny or no deposits
- Possibly bot-like or abandoned wallets

---

### 🟧 Wallets in 100–300
- Minimal engagement or incomplete loan cycles
- Low diversity in asset interactions
- Most common range among observed users

---

### 🟨 Wallets in 500–1000
- Strong participation with successful loan cycles
- Good asset variety and high USD flow
- Strategic usage patterns with less frequent interactions

---

### 🟢 Power Users (900–1000)
- Reliable, repeat users with no liquidations
- High value, high frequency, full-cycle DeFi users
- Likely professionals or institutions

---

## ✅ Conclusion

The credit scoring pipeline successfully differentiates between risky, average, and responsible wallets in a transparent and interpretable manner. It's suitable for:

- **DeFi Lending Platforms**: to assess borrower credibility  
- **Wallet Trust Indexing**: e.g., for airdrops, voting, or DAO access  
- **Risk Engines**: in dApps or protocols

---

## 💡 Future Enhancements

- Time-decayed scores (recent actions weigh more)
- Incorporating token volatility/risk weights
- Integrating on-chain identities (ENS, POAP, Gitcoin Passport)
