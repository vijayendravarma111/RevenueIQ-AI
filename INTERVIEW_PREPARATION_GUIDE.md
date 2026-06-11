# RevenueIQ AI – Master Interview Preparation Guide

This guide is designed to prepare you to discuss **RevenueIQ AI** with 100% confidence in data science, machine learning, and business intelligence interviews. It covers the project's purpose, methodologies, mathematical concepts, code implementations, and key interview questions.

---

## SECTION 1: Project Overview

### What is RevenueIQ AI?
**RevenueIQ AI** is a data science and machine learning dashboard that helps retail managers optimize their store sales, analyze customer buying patterns, and manage inventory stock levels. It connects forecasting predictions directly with warehouse inventory levels to make real-world business decisions.

### What Business Problems Does It Solve?
1. **Inventory Waste vs. Stockouts**: If a retail store stocks too much inventory, they waste money on storage and unsold goods. If they stock too little, they lose customers. The **Prophet Forecasting Model** predicts 90 days of demand to help the store order the exact amount of stock required.
2. **Identifying Revenue Drivers**: Retailers need to know if promotions, holidays, or competition affect their daily sales. The **XGBoost Regressor Model** ranks these features by importance, showing exactly what drives sales.
3. **Targeting Marketing Campaigns**: Instead of treating all customers the same, the **K-Means Clustering Model** groups customers into VIP Champions, Frequent Buyers, Regular Customers, and Low-Value Cohorts. This allows targeted marketing campaigns.

### The Datasets Used
* **Rossmann Store Sales Dataset**: Daily sales transactions from 1,115 stores across Europe. Used for demand forecasting (Prophet) and sales driver analysis (XGBoost).
* **Superstore Transaction Dataset**: Transactional data containing product inventory categories, sales quantities, and customer IDs. Used for customer segmentation (K-Means) and inventory cover planning.

---

## SECTION 2: Deep-Dive into Machine Learning Models

---

### MODEL 1: Facebook Prophet (Demand Forecasting)

#### 1. Why use Prophet?
Prophet is a time-series forecasting library developed by Meta. It is preferred over traditional methods (like ARIMA) or deep learning (like LSTMs) because:
* It handles strong **yearly and weekly seasonality** automatically.
* It easily incorporates **holiday schedules** (e.g., Christmas, school holidays).
* It is robust to missing data and trend shifts.
* It requires minimal tuning while producing high-quality business forecasts.

#### 2. How it works mathematically
Prophet models time series as an additive regression model with three main components:
$$y(t) = g(t) + s(t) + h(t) + \epsilon_t$$
* **$g(t)$ (Trend)**: Captures non-periodic, long-term changes in sales (e.g., store growth).
* **$s(t)$ (Seasonality)**: Captures periodic changes (e.g., weekly closures, yearly holiday cycles).
* **$h(t)$ (Holidays)**: Captures the irregular impacts of holiday events on sales.
* **$\epsilon_t$ (Error)**: Captures random fluctuations that the model cannot explain.

#### 3. Log-Transformation ($y_{log} = \log(y + 1)$)
* **Why do we do this?** Retail sales have high variance (extreme spikes on Saturdays/promotions and zeros on Sundays). Logging the target compresses this variance, making it easier for the model to train. It also prevents the model from predicting negative sales (which is physically impossible).
* **Inverse Transform**: Since the model predicts in the log scale ($\hat{y}_{log}$), we must convert it back to the original currency scale before showing it to users:
  $$\text{predicted\_sales} = e^{\hat{y}_{log}} - 1$$

#### 4. WMAPE vs. MAPE (Critical Interview Point)
* **MAPE (Mean Absolute Percentage Error)**:
  $$\text{MAPE} = \frac{100\%}{n} \sum_{t=1}^{n} \left| \frac{y_t - \hat{y}_t}{y_t} \right|$$
  * *The Issue*: If actual sales ($y_t$) are zero or very low (e.g., Sundays or holidays), dividing by $y_t$ results in division by zero or extreme spikes in error. This is why our raw daily MAPE was **62.4%**.
* **WMAPE (Volume-Weighted MAPE)**:
  $$\text{WMAPE} = \frac{\sum |y_t - \hat{y}_t|}{\sum y_t} \times 100\%$$
  * *The Solution*: Instead of averaging percentages, WMAPE sums the absolute errors and divides by the total sales volume. This avoids division-by-zero errors on closed days and weights error by sales importance. Our validation WMAPE is **22.60%** (meaning **77.4%** forecast accuracy).

#### 5. Important Code Snippet
```python
# Train/Test Split (Chronological 90-day holdout)
split_date = daily_sales["ds"].max() - pd.Timedelta(days=90)
train_prophet = daily_sales[daily_sales["ds"] <= split_date].copy()
test_prophet = daily_sales[daily_sales["ds"] > split_date].copy()

# Fit validation model on logged targets
val_model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
train_input = train_prophet[["ds", "y_log"]].rename(columns={"y_log": "y"})
val_model.fit(train_input)

# Forecast and inverse transform back to normal sales
val_forecast = val_model.predict(test_prophet[["ds"]])
val_forecast["predicted_sales"] = np.expm1(val_forecast["yhat"]).clip(lower=0)
```

---

### MODEL 2: XGBoost Regressor (Sales Driver Analysis)

#### 1. Why use XGBoost?
XGBoost (eXtreme Gradient Boosting) is a decision-tree-based ensemble algorithm. It is chosen because:
* It outperforms neural networks on tabular datasets.
* It captures non-linear relationships (e.g., competitor distance matters, but its effect drops off after a certain threshold).
* It provides **Feature Importances**, showing exactly which variables (e.g., promos) impact sales the most.

#### 2. Data Leakage Resolution (Your Biggest Interview Story)
* **What was the leakage?** In the initial model, features like `Customers` and `SalesPerCustomer` (calculated as $\frac{\text{Sales}}{\text{Customers}}$) were used to predict `Sales`. This circular dependency yielded a fake $R^2 = 0.9989$.
* **Why is it leakage?** When predicting future sales next month, you do not know the exact customer count or how much each customer will spend on that day.
* **The Fix**: We completely removed `Customers` and `SalesPerCustomer`. The model now uses only features available at forecast time (Promotions, Holidays, Calendar features, Competition Distance). The $R^2$ dropped to an honest, interview-defensible **0.6813**.

#### 3. Important Code Snippet
```python
# XGBoost features without leakage
xgb_features = [
    "DayOfWeek", "PromoActive", "IsHoliday", "IsSchoolHoliday", 
    "CompetitionDistance", "CompetitionAge", "IsWeekend", 
    "MonthStart", "MonthEnd", "Promo2SinceWeek", "Year", "Month", "Day"
]

X = train_store[xgb_features]
y = train_store["Sales"]

# Chronological Train-Test Split (e.g., 80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

model = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, subsample=0.8)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

---

### MODEL 3: K-Means Clustering (Customer Segmentation)

#### 1. What is RFM Analysis?
RFM is a classic marketing framework:
* **Recency**: How recently did the customer purchase?
* **Frequency**: How often do they purchase?
* **Monetary**: How much do they spend?
In our K-Means model, we cluster customers using four aggregate variables: `total_sales`, `total_orders` (frequency), `total_quantity`, and `total_profit`.

#### 2. Feature Scaling (`StandardScaler`)
* **Why is it required?** K-Means relies on **Euclidean Distance** to group data points:
  $$d(p, q) = \sqrt{\sum (p_i - q_i)^2}$$
  If one feature is in thousands (e.g., `total_sales` = \$5,000) and another is in units (e.g., `total_orders` = 3), the sales feature will dominate the distance calculations. `StandardScaler` standardizes each feature to have a mean of 0 and variance of 1, ensuring all metrics are treated equally:
  $$z = \frac{x - \mu}{\sigma}$$

#### 3. Determining the Optimal Number of Clusters ($K=4$)
* **Elbow Method (Inertia/WCSS)**: Sum of squared distances of samples to their closest cluster center. We plot WCSS against $K$ and find the "elbow" where adding more clusters yields diminishing returns.
* **Silhouette Score**: Measures how similar an object is to its own cluster compared to other clusters. It ranges from -1 to +1. Our model achieves a Silhouette Score of **0.2969**, showing clear cluster division.

#### 4. The 4 Customer Segments
* **VIP Champions (Segment 1)**: High purchase frequency, high profit contribution, high spend. (Strategy: VIP loyalty benefits).
* **Frequent Buyers (Segment 2)**: Very high order count and volume, moderate profit margin. (Strategy: Cross-sell high-margin products).
* **Regular Customers (Segment 0)**: Average spend and frequency. (Strategy: Nurture with targeted email campaigns).
* **Low-Value Customers (Segment 3)**: Low spend and frequency. (Strategy: Offer discount coupon triggers).

#### 5. Important Code Snippet
```python
# Scale the RFM metrics
scaler = StandardScaler()
scaled_features = scaler.fit_transform(customer_features[["total_sales", "total_profit", "total_quantity", "total_orders"]])

# Train KMeans
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
customer_features["segment"] = kmeans.fit_predict(scaled_features)
```

---

## SECTION 3: Operations & Inventory Integration

### Forecast-Driven Stock Run-Out (Days to Stockout)
Instead of simply warning managers when stock is low, the platform dynamically connects forecasting predictions to individual product stock levels.
1. **Expected Growth Factor**: The forecasting model calculates expected growth ($\text{growth}\%$) for the upcoming 90 days.
2. **Forecasted Daily Velocity**: The historical daily sales velocity of each item is scaled by the growth factor:
   $$\text{Forecasted Daily Velocity} = \text{Historical Daily Sales Velocity} \times \left(1 + \frac{\text{growth}\%}{100}\right)$$
3. **Estimated Days of Cover**:
   $$\text{Days to Stockout} = \frac{\text{Current Stock}}{\text{Forecasted Daily Velocity}}$$
4. **Actionable Alerts**: If $\text{Days to Stockout} < 15$ days, the product is flagged as **Critical Run-Out**; if $15 \leq \text{Days to Stockout} < 30$, it is flagged as **Run-Out Risk**.

---

## SECTION 4: Top 20 Interview Questions & Answers

### Q1: Can you describe the overall architecture of this project?
> **Answer**: Yes. The project is built on a modular three-tier architecture:
> 1. **Data Layer**: Raw datasets (Rossmann store sales and Superstore transactions) stored in CSV files, with connection hooks available for MySQL.
> 2. **Intelligence Layer**: A centralized automation script (`run_pipeline.py`) that handles all preprocessing, target scaling, model fitting (Prophet, XGBoost, K-Means), holdout validation, and serializes the model files (`.pkl`) and dynamic metrics logs.
> 3. **Presentation Layer**: An interactive Streamlit dashboard consisting of a Command Center (KPI overview), Demand Intelligence (sales forecasting), Revenue Drivers (XGBoost importance), Customer Insights (RFM segmentation), and Inventory Analytics (safety stock run-out coverage).

### Q2: Why did you choose Facebook Prophet for forecasting instead of LSTM or ARIMA?
> **Answer**: I chose Prophet because it is highly optimized for daily retail transactions. Traditional models like ARIMA assume stationarity and struggle with calendar features and holiday spikes. Recurrent neural networks like LSTMs require vast amounts of data and are difficult to tune. Prophet handles strong yearly and weekly seasonality (like Sunday closures) and holiday dates out-of-the-box, making it the most robust choice for business demand forecasting.

### Q3: What is data leakage and how did you resolve it in this project?
> **Answer**: Data leakage occurs when a model is trained using features that contain information about the target variable which would not actually be available at prediction time. In the initial implementation of the XGBoost model, the features `Customers` and `SalesPerCustomer` were included to predict `Sales`. Since `SalesPerCustomer` is calculated as $\text{Sales} / \text{Customers}$, this was a circular feature.
> I resolved this by removing both features from the pipeline. The updated model uses only parameters known in advance (calendar dates, promotional flags, competition distance, holiday schedules). This reduced the $R^2$ from a fake $0.9989$ to an honest and realistic $0.6813$.

### Q4: Why is WMAPE preferred over MAPE in this project?
> **Answer**: Retail transactions are highly volatile and drop to zero on Sundays or holidays due to store closures. If actual sales are zero, calculating MAPE causes division by zero. If actual sales are very small, MAPE shoots up to infinity.
> WMAPE (Volume-Weighted MAPE) solves this by summing absolute errors across all days and dividing by the sum of actual sales volume. It avoids division-by-zero errors, handles low-volume days, and represents the true aggregate forecasting accuracy (77.4%) much better than raw daily MAPE (62.4% error).

### Q5: How did you validate your forecasting model to prevent lookahead bias?
> **Answer**: I used a chronological holdout validation split rather than a random train/test split. Since time-series data is sequential, random splitting would cause lookahead bias (training on future data to predict the past). I split the daily sales chronologically, training the Prophet validation model on all data up to the last 90 days, and evaluated its performance strictly on the unseen final 90 days.

### Q6: Why did you apply a log-transformation to the sales target in Prophet?
> **Answer**: Sales data often exhibits non-constant variance (heteroscedasticity)—variance increases as sales volume grows. Applying a natural log transformation ($y_{log} = \log(y + 1)$) stabilizes this variance, compresses extreme holiday sales spikes, and guarantees that the model will never predict negative sales values. We then apply an exponential inverse transformation ($e^{\hat{y}} - 1$) to convert predictions back to the currency scale.

### Q7: Why is feature scaling necessary for K-Means clustering?
> **Answer**: K-Means clustering calculates Euclidean distances between data points to group them. If features have different scales (e.g. `total_sales` in thousands vs `total_orders` in single digits), the feature with the larger range will dominate the distance calculation. I used `StandardScaler` to scale the features to have a mean of 0 and standard deviation of 1, ensuring all RFM metrics contribute equally to the clusters.

### Q8: What does a Silhouette Score of 0.297 represent for K-Means?
> **Answer**: The Silhouette Score measures how close each point is to points in its own cluster compared to points in other clusters. It ranges from -1 (poor clustering) to +1 (perfect clustering). A score of **0.297** indicates that the customer segments are distinct and reasonably separated, which is a very normal and acceptable score for real-world customer transactional datasets with high noise.

### Q9: Can you explain the K-Means cluster composition?
> **Answer**: Yes. I grouped the customer base into 4 segments:
> 1. **VIP Champions (Segment 1)**: Represent a small percentage of customers but contribute the majority of revenue and profit.
> 2. **Frequent Buyers (Segment 2)**: Purchase very frequently and buy high volumes, but have moderate margins.
> 3. **Regular Customers (Segment 0)**: Have average spends and moderate order frequencies.
> 4. **Low-Value Customers (Segment 3)**: Low order count and low spending.

### Q10: How did you connect your forecasting model to the inventory planning?
> **Answer**: I calculated the average daily sales velocity of each product from transaction histories, and scaled this velocity by the forecasting model's expected growth rate for the next 90 days. I then divided each item's current stock level by this forecasted daily unit velocity to estimate the **Days to Stockout**. This allows managers to identify stockout risks based on future market demand rather than static historical averages.

### Q11: What features are the strongest revenue drivers in your XGBoost model?
> **Answer**: The strongest driver of revenue is promotions (`PromoActive`), followed closely by competitor factor features (e.g. `CompetitionDistance` and `CompetitionAge`). This tells the business that promotional activities have the most immediate impact on sales, while distance to competitors acts as a secondary pressure.

### Q12: Why did you remove the Supplier and Pricing Intelligence features?
> **Answer**: Supplier and Pricing sections relied on basic SQL-style database aggregations (averaging competitor prices and supplier lead times) without any statistical modeling or machine learning components. Removing them keeps the repository tightly focused on the core ML story (Forecasting, Regression, Clustering), simplifying the technical narrative and reducing interviewer distraction.

### Q13: What does the Business Health Score represent?
> **Answer**: The Business Health Score is a composite, calculated index representing overall retail health:
> $$\text{Health Score} = 0.4 \times (3 \times \text{Profit Margin}\%) + 0.3 \times \text{Forecast Accuracy}\% + 0.3 \times \text{Inventory Health}\%$$
> It combines profitability (margin), demand forecasting reliability, and stock availability to give executives a single, data-driven score of operations.

### Q14: How did you handle Sunday store closures in your forecasting model?
> **Answer**: Stores in Germany are closed on Sundays due to local laws. This causes sales to drop to zero once a week. Prophet captures this automatically by fitting a weekly seasonality component ($s(t)$). I also added a caption below the forecast chart to explain to recruiters that these weekly drops are expected operational patterns, not data artifacts.

### Q15: How does your pipeline ensure reproducibility?
> **Answer**: All preprocessing, modeling, evaluation, and data export steps are encapsulated in `run_pipeline.py`. Anyone can clone the repository, run `python run_pipeline.py`, and completely recreate all serialized models, metrics files, and dashboard datasets.

### Q16: How did you handle missing values in your datasets?
> **Answer**: In the Rossmann store metadata, `CompetitionDistance` had missing values. I imputed these using the median distance ($2,325\text{m}$) because distance is right-skewed and the median is robust to outliers. Other missing values in competitor open dates were zero-filled to indicate no active competition.

### Q17: What was the biggest technical challenge you faced in this project?
> **Answer**: The biggest challenge was aligning the metrics and resolving the target leakage in the XGBoost model. Once the target leakage was resolved by removing `Customers`, the R² score dropped from a fake $0.9989$ to $0.6813$. While the score was lower, explaining this audit to a recruiter shows a strong understanding of machine learning principles, data leakage, and real-world deployment challenges.

### Q18: What programming stack did you use to build the dashboard?
> **Answer**: I used Python as the core language. Data engineering was done using Pandas and NumPy. Machine learning was built with XGBoost and Scikit-Learn. Forecasting was done using Prophet. The visualization and UI were implemented using Streamlit, Plotly, HTML5, and CSS3.

### Q19: Why did you rename the "AI Executive Summary" to "Executive Summary"?
> **Answer**: To maintain absolute technical honesty. I want to show recruiters that I only brand a feature as "AI" if it uses actual Large Language Models (LLMs) or complex deep learning reasoning. The executive summary is generated from actual calculations and model outputs, so "Executive Summary" is the correct, honest term.

### Q20: If you had more time, what is the next step to improve this project?
> **Answer**: I would implement a closed-loop inventory replenishment model (e.g., using reinforcement learning or operations research solvers) to automatically generate optimal order quantities and schedules for each warehouse based on the Prophet demand forecasts, replacing the simple stock run-out rule.
