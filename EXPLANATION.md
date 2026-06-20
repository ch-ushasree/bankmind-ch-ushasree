# Explanation

## Track A: Data Analyst

### 1. What percentage of customers in your dataset have `y = yes`? What does this imbalance mean for how you would evaluate a model?

In `bank-full.csv`, 5,289 out of 45,211 customers subscribed, which is 11.70% of the dataset. This means the target is imbalanced: most customers did not subscribe. If I later built a model, accuracy alone would be misleading because a model could predict "no" for almost everyone and still appear strong. I would also check precision, recall, F1-score, and ROC-AUC so the evaluation focuses on finding real subscribers, not just the majority class.

### 2. Which job category had the highest subscription rate? Does this make sense to you intuitively?

The `student` category had the highest subscription rate at 28.68%: 269 subscriptions from 938 student customers. This makes intuitive sense because students may be more open to new banking products, especially starter accounts, cards, or savings products. However, the segment is relatively small, so an RM should also consider larger segments like management, which has a lower rate but many more total customers.

### 3. Which job types have the highest subscription rate?

The top job categories by subscription rate are students, retired customers, unemployed customers, and management customers. I used subscription rate instead of raw subscriber count because raw counts can overstate large groups and hide smaller high-conversion segments. This is useful for RMs because it separates "high chance of conversion" from only "large customer volume."

### 4. Is there a pattern between account balance and likelihood to subscribe?

Yes. Customers with negative balances had the lowest subscription rate at about 5.58%, while customers in the 1,501-5,000 balance band had a much stronger rate at about 16.61%. This suggests that customers with healthier deposit relationships may be better timed for cross-sell outreach.

### 5. How does subscription rate differ across age groups?

The 60+ age group had the highest subscription rate at about 42.26%, while the 31-45 and 46-60 groups were both below 10%. The 18-30 group also performed better than the middle-age groups at about 16.29%. This indicates that age is useful, but it should be combined with other signals like job, balance, and loan status before making a recommendation.

### 6. Does having an existing housing loan make someone less likely to take a new product?

Yes. Customers with a housing loan subscribed at about 7.70%, while customers without a housing loan subscribed at about 16.70%. This is a strong difference and suggests that existing debt commitments may reduce appetite for additional banking products, or that the timing of the offer matters more for those customers.

### 7. What additional RM insight did you add beyond the basic housing-loan question?

I also broke customers into four debt profiles using both `housing` and `loan`. The exact subscription rates are: no housing loan and no personal loan at 18.22%, no housing loan with a personal loan at 7.61%, housing loan with no personal loan at 8.04%, and both housing plus personal loan at 6.07%. This is more useful for an RM than only saying "housing loans are bad," because it shows debt-free customers are the strongest outreach group while customers carrying two loan commitments should usually be deprioritized.

### 8. What did you build?

I built a Streamlit dashboard for Relationship Managers to explore cross-sell opportunities in the UCI Bank Marketing Dataset. The app uses tabs to separate exploratory analysis, the daily RM priority list, and data health/raw samples, so repeated users do not need to scroll past every chart just to reach the call-planning table. The priority-segment table ranks customer groups using subscription rate, average balance, and segment size. The priority score is an analytical heuristic, not a trained ML model, so it is meant to support business exploration rather than replace model-based prediction.
