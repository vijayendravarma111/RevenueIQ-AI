import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from prophet import Prophet


# --------------------------------------------------
# CONFIG & PATHS
# --------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
KPI_DIR = PROCESSED_DIR / "dashboard"
MODELS_DIR = ROOT_DIR / "models"

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
KPI_DIR.mkdir(parents=True, exist_ok=True)
(MODELS_DIR / "prophet").mkdir(parents=True, exist_ok=True)
(MODELS_DIR / "xgboost").mkdir(parents=True, exist_ok=True)
(MODELS_DIR / "kmeans").mkdir(parents=True, exist_ok=True)


print("Starting RevenueIQ AI Data Science & Machine Learning Pipeline...")

# =====================================================================
# STEP 1: DATA CLEANING & PREPROCESSING
# =====================================================================
print("\n--- Step 1: Cleaning and Preprocessing Data ---")

# Load Raw Data
train = pd.read_csv(RAW_DIR / "train.csv", low_memory=False)
store = pd.read_csv(RAW_DIR / "store.csv", low_memory=False)
superstore = pd.read_csv(RAW_DIR / "Superstore.csv", encoding="latin1", low_memory=False)

# Clean date columns
train["Date"] = pd.to_datetime(train["Date"], errors="coerce")
superstore["Order Date"] = pd.to_datetime(superstore["Order Date"], errors="coerce")
superstore["Ship Date"] = pd.to_datetime(superstore["Ship Date"], errors="coerce")

# Clean Store metadata
store_clean = store.copy()
store_clean["CompetitionDistance"] = store_clean["CompetitionDistance"].fillna(
    store_clean["CompetitionDistance"].median()
)
store_clean["CompetitionOpenSinceMonth"] = store_clean["CompetitionOpenSinceMonth"].fillna(0)
store_clean["CompetitionOpenSinceYear"] = store_clean["CompetitionOpenSinceYear"].fillna(0)
store_clean["Promo2SinceWeek"] = store_clean["Promo2SinceWeek"].fillna(0)
store_clean["Promo2SinceYear"] = store_clean["Promo2SinceYear"].fillna(0)
store_clean["PromoInterval"] = store_clean["PromoInterval"].fillna("No Promo")

# Merge Train with Store Metadata
train_store = train.merge(store_clean, on="Store", how="left")

# =====================================================================
# STEP 2: FEATURE ENGINEERING
# =====================================================================
print("\n--- Step 2: Feature Engineering ---")

train_store["Year"] = train_store["Date"].dt.year
train_store["Month"] = train_store["Date"].dt.month
train_store["Day"] = train_store["Date"].dt.day
train_store["Week"] = train_store["Date"].dt.isocalendar().week.astype(int)
train_store["Quarter"] = train_store["Date"].dt.quarter

train_store["IsWeekend"] = train_store["DayOfWeek"].isin([6, 7]).astype(int)

# Competition Age
train_store["CompetitionAge"] = train_store["Year"] - train_store["CompetitionOpenSinceYear"]
train_store["CompetitionAge"] = train_store["CompetitionAge"].clip(lower=0)

# Promo Active
train_store["PromoActive"] = (train_store["Promo"] > 0).astype(int)

# State Holiday flags (StateHoliday is string or int, we standardise it)
train_store["IsHoliday"] = (train_store["StateHoliday"].astype(str) != "0").astype(int)

# School Holiday flag
train_store["IsSchoolHoliday"] = train_store["SchoolHoliday"].astype(int)

# Month boundary indicators
train_store["MonthStart"] = train_store["Date"].dt.is_month_start.astype(int)
train_store["MonthEnd"] = train_store["Date"].dt.is_month_end.astype(int)

# Note: SalesPerCustomer is kept for general historical reporting in the dataset,
# but it WILL be excluded from XGBoost features to prevent target leakage.
train_store["SalesPerCustomer"] = train_store["Sales"] / train_store["Customers"].replace(0, np.nan)
train_store["SalesPerCustomer"] = train_store["SalesPerCustomer"].fillna(0)

# Export cleaned files
train_store.to_csv(PROCESSED_DIR / "rossmann_clean.csv", index=False)
superstore.to_csv(PROCESSED_DIR / "superstore_clean.csv", index=False)
print("Saved cleaned datasets to data/processed/")


# =====================================================================
# STEP 3: DEMAND FORECASTING (PROPHET)
# =====================================================================
print("\n--- Step 3: Demand Forecasting (Prophet) ---")

daily_sales = train_store.groupby("Date")["Sales"].sum().reset_index()
daily_sales.columns = ["ds", "y"]

# Log transform target for variance stabilization and additive seasonality performance
daily_sales["y_log"] = np.log1p(daily_sales["y"])

# Train/Test Split (last 90 days for testing forecasting performance)
split_date = daily_sales["ds"].max() - pd.Timedelta(days=90)
train_prophet = daily_sales[daily_sales["ds"] <= split_date].copy()
test_prophet = daily_sales[daily_sales["ds"] > split_date].copy()

# Fit validation model
print("Training Prophet validation model...")
val_model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)
# Use y_log as training target
train_prophet_input = train_prophet[["ds", "y_log"]].rename(columns={"y_log": "y"})
val_model.fit(train_prophet_input)

# Predict on test period
val_forecast = val_model.predict(test_prophet[["ds"]])
val_forecast["predicted_sales"] = np.expm1(val_forecast["yhat"]).clip(lower=0)


# Evaluate
y_true = test_prophet["y"].values
y_pred = val_forecast["predicted_sales"].values

# Avoid divide by zero
mask = y_true > 0
p_true = y_true[mask]
p_pred = y_pred[mask]

prophet_mae = mean_absolute_error(p_true, p_pred)
prophet_rmse = np.sqrt(mean_squared_error(p_true, p_pred))
prophet_mape = np.mean(np.abs((p_true - p_pred) / p_true)) * 100
prophet_r2 = r2_score(y_true, y_pred)
prophet_wmape = np.sum(np.abs(y_true - y_pred)) / np.sum(y_true) * 100

print(f"Prophet Forecasting Test-Set Evaluation (Last 90 Days):")
print(f"  MAE : ${prophet_mae:,.2f}")
print(f"  RMSE: ${prophet_rmse:,.2f}")
print(f"  MAPE: {prophet_mape:.2f}%")
print(f"  WMAPE: {prophet_wmape:.2f}%")
print(f"  R2  : {prophet_r2:.4f}")

# Save Prophet metrics
prophet_metrics = {
    "MAE": prophet_mae,
    "RMSE": prophet_rmse,
    "MAPE": prophet_mape,
    "WMAPE": prophet_wmape,
    "R2": prophet_r2
}
with open(MODELS_DIR / "prophet" / "prophet_metrics.json", "w") as f:
    json.dump(prophet_metrics, f, indent=4)

# Train Final Model on all data
print("Training final Prophet model on full time series...")
final_prophet = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)
final_prophet.fit(daily_sales[["ds", "y_log"]].rename(columns={"y_log": "y"}))

future = final_prophet.make_future_dataframe(periods=90)
forecast = final_prophet.predict(future)

forecast["predicted_sales"] = np.expm1(forecast["yhat"]).clip(lower=0)
forecast["lower_sales"] = np.expm1(forecast["yhat_lower"]).clip(lower=0)
forecast["upper_sales"] = np.expm1(forecast["yhat_upper"]).clip(lower=0)


# Save Final Forecast and Model
joblib.dump(final_prophet, MODELS_DIR / "prophet" / "prophet_model.pkl")
forecast.to_csv(MODELS_DIR / "prophet" / "forecast.csv", index=False)
print("Saved Prophet models and forecasts.")


# =====================================================================
# STEP 4: REVENUE DRIVER ANALYSIS (XGBOOST REGRESSOR)
# =====================================================================
print("\n--- Step 4: Revenue Driver Analysis (XGBoost) ---")
print("Removing target-leaking features ('Customers' & 'SalesPerCustomer')...")

# Features list (CLEANED, leakage-free)
xgb_features = [
    "DayOfWeek",
    "Promo",
    "SchoolHoliday",
    "CompetitionDistance",
    "Promo2",
    "Year",
    "Month",
    "Week",
    "Quarter",
    "IsWeekend",
    "CompetitionAge",
    "PromoActive",
    "IsHoliday",
    "IsSchoolHoliday",
    "MonthStart",
    "MonthEnd"
]

# Extract data
X = train_store[xgb_features]
y = train_store["Sales"]

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Import XGBoost
from xgboost import XGBRegressor

print("Training XGBoost Regressor model...")
xgb_model = XGBRegressor(
    n_estimators=100,  # Optimized for execution speed and accuracy
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)
xgb_model.fit(X_train, y_train)

# Evaluate on test set
xgb_preds = xgb_model.predict(X_test)
xgb_mae = mean_absolute_error(y_test, xgb_preds)
xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_preds))
xgb_r2 = r2_score(y_test, xgb_preds)

print(f"XGBoost Test-Set Evaluation (Leakage-Free):")
print(f"  MAE : ${xgb_mae:,.2f}")
print(f"  RMSE: ${xgb_rmse:,.2f}")
print(f"  R²  : {xgb_r2:.4f}")

# Save feature importances
importance = pd.DataFrame({
    "Feature": xgb_features,
    "Importance": xgb_model.feature_importances_
}).sort_values(by="Importance", ascending=False)

importance.to_csv(MODELS_DIR / "xgboost" / "feature_importance.csv", index=False)

# Save XGBoost model and metrics
joblib.dump(xgb_model, MODELS_DIR / "xgboost" / "xgboost_model.pkl")
xgb_metrics = {
    "MAE": xgb_mae,
    "RMSE": xgb_rmse,
    "R2": xgb_r2
}
with open(MODELS_DIR / "xgboost" / "xgboost_metrics.json", "w") as f:
    json.dump(xgb_metrics, f, indent=4)
print("Saved XGBoost model and feature importances.")


# =====================================================================
# STEP 5: CUSTOMER SEGMENTATION (KMEANS)
# =====================================================================
print("\n--- Step 5: Customer Segmentation (K-Means) ---")

# RFM Aggregation
customer_features = superstore.groupby("Customer ID").agg({
    "Sales": "sum",
    "Profit": "sum",
    "Quantity": "sum",
    "Order ID": "nunique"
}).reset_index()

customer_features.columns = [
    "customer_id",
    "total_sales",
    "total_profit",
    "total_quantity",
    "total_orders"
]

# Scale features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(
    customer_features[["total_sales", "total_profit", "total_quantity", "total_orders"]]
)

# KMeans Clustering
print("Fitting K-Means model (K=4)...")
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
customer_features["segment"] = kmeans.fit_predict(scaled_features)

# Compute Silhouette Score on sample to save memory/computation
sample_size = min(len(scaled_features), 5000)
sh_score = silhouette_score(scaled_features, customer_features["segment"])
inertia = kmeans.inertia_

print(f"K-Means Clustering Diagnostics:")
print(f"  Silhouette Score: {sh_score:.4f}")
print(f"  Inertia (WCSS)  : {inertia:,.2f}")

# Save KMeans Model and Data
joblib.dump(kmeans, MODELS_DIR / "kmeans" / "kmeans_model.pkl")
customer_features.to_csv(MODELS_DIR / "kmeans" / "customer_segments.csv", index=False)

kmeans_metrics = {
    "SilhouetteScore": sh_score,
    "Inertia": inertia
}
with open(MODELS_DIR / "kmeans" / "kmeans_metrics.json", "w") as f:
    json.dump(kmeans_metrics, f, indent=4)
print("Saved K-Means model and segmented customer data.")



# =====================================================================
# STEP 6: GENERATING DASHBOARD DATASETS
# =====================================================================
print("\n--- Step 6: Exporting Dashboard Datasets & KPIs ---")


# Executive KPIs from Superstore
exec_kpis = pd.DataFrame({
    "Metric": ["Total Revenue", "Total Customers", "Total Orders", "Total Profit"],
    "Value": [
        superstore["Sales"].sum(),
        superstore["Customer ID"].nunique(),
        superstore["Order ID"].nunique(),
        superstore["Profit"].sum()
    ]
})
exec_kpis.to_csv(KPI_DIR / "executive_kpis.csv", index=False)

# Monthly Revenue for Trend Plotting
revenue_kpis = superstore.groupby("Order Date")["Sales"].sum().reset_index()
revenue_kpis.to_csv(KPI_DIR / "revenue_kpis.csv", index=False)

# Segment Average Metrics
customer_kpis = customer_features.groupby("segment").agg({
    "total_sales": "mean",
    "total_profit": "mean",
    "total_orders": "mean"
}).reset_index()
customer_kpis.to_csv(KPI_DIR / "customer_kpis.csv", index=False)

# Customer Segment Counts
segment_counts = customer_features["segment"].value_counts().reset_index()
segment_counts.columns = ["segment", "count"]
segment_counts.to_csv(KPI_DIR / "segment_counts.csv", index=False)

# Prophet Forecast metrics
forecast_kpis = forecast[["ds", "yhat"]]
forecast_kpis.to_csv(KPI_DIR / "forecast_kpis.csv", index=False)
forecast.tail(90).to_csv(KPI_DIR / "forecast_90_days.csv", index=False)
forecast.to_csv(KPI_DIR / "full_forecast.csv", index=False)

# Save feature importances as revenue drivers
importance.to_csv(KPI_DIR / "revenue_drivers.csv", index=False)



# Full files copy for pages reading
customer_features.to_csv(KPI_DIR / "customer_segments_full.csv", index=False)

# Inventory KPI generation from external data and Superstore demand velocity
total_days = max(1, (superstore["Order Date"].max() - superstore["Order Date"].min()).days)
product_qty = superstore.groupby("Product ID")["Quantity"].sum().reset_index()
product_qty["daily_velocity"] = product_qty["Quantity"] / total_days

inventory = pd.read_csv(ROOT_DIR / "data" / "external" / "inventory_data.csv")
inventory = inventory.merge(
    product_qty[["Product ID", "daily_velocity"]].rename(columns={"Product ID": "product_id"}),
    on="product_id",
    how="left"
)
inventory["daily_velocity"] = inventory["daily_velocity"].fillna(inventory["daily_velocity"].median())
inventory["daily_velocity"] = inventory["daily_velocity"].clip(lower=0.01)
inventory.to_csv(KPI_DIR / "inventory_full.csv", index=False)

inventory_kpis = pd.DataFrame({
    "Total Products": [inventory["product_id"].nunique()],
    "Total Stock": [inventory["current_stock"].sum()],
    "Average Stock": [inventory["current_stock"].mean()]
})
inventory_kpis.to_csv(KPI_DIR / "inventory_kpis.csv", index=False)

# Competitors Data copy
competitors = pd.read_csv(ROOT_DIR / "data" / "external" / "competitor_data.csv")
competitors.to_csv(KPI_DIR / "competitor_full.csv", index=False)

# Top Products & Top Customers for Dashboard Champions
top_products = superstore.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(20).reset_index()
top_products.to_csv(KPI_DIR / "top_products.csv", index=False)

top_customers = superstore.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(20).reset_index()
top_customers.to_csv(KPI_DIR / "top_customers.csv", index=False)

print("\nAll datasets and KPIs successfully exported to data/processed/dashboard/.")
print("DATA SCIENCE PIPELINE COMPLETE SUCCESS!")
