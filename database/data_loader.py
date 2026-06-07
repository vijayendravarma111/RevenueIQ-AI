from pathlib import Path

import pandas as pd

from database.mysql_connection import get_engine


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

ROSSMANN_PATH = (
    ROOT_DIR /
    "data" /
    "processed" /
    "rossmann_clean.csv"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

rossmann = pd.read_csv(
    ROSSMANN_PATH,
    low_memory=False
)

print("Data Loaded")


# --------------------------------------------------
# MYSQL
# --------------------------------------------------

engine = get_engine()

print("Connected to MySQL")


# --------------------------------------------------
# STORES TABLE
# --------------------------------------------------

stores = rossmann[
    [
        "Store",
        "StoreType",
        "Assortment",
        "CompetitionDistance",
        "Promo2"
    ]
].drop_duplicates(
    subset=["Store"]
)

stores.columns = [
    "store_id",
    "store_type",
    "assortment",
    "competition_distance",
    "promo2"
]

print("Stores Shape:", stores.shape)

stores.to_sql(
    "stores",
    con=engine,
    if_exists="replace",
    index=False
)

print("Stores Loaded")


# --------------------------------------------------
# SALES TABLE
# --------------------------------------------------

sales = rossmann[
    [
        "Store",
        "Date",
        "Sales",
        "Customers",
        "Promo",
        "IsHoliday",
        "IsSchoolHoliday"
    ]
]

sales.columns = [
    "store_id",
    "sale_date",
    "sales",
    "customers",
    "promo",
    "holiday",
    "school_holiday"
]

print("Sales Shape:", sales.shape)

sales.to_sql(
    "sales",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=10000
)

print("Sales Loaded")

print("SUCCESS")

SUPERSTORE_PATH = (
    ROOT_DIR /
    "data" /
    "processed" /
    "superstore_clean.csv"
)

superstore = pd.read_csv(
    SUPERSTORE_PATH,
    encoding="latin1",
    low_memory=False
)

print("Superstore Loaded")

customers = superstore[
[
    "Customer ID",
    "Customer Name",
    "Segment",
    "City",
    "State",
    "Region"
]]

customers = customers.drop_duplicates(
    subset=["Customer ID"]
)

customers.columns = [
    "customer_id",
    "customer_name",
    "segment",
    "city",
    "state",
    "region"
]

customers.to_sql(
    "customers",
    con=engine,
    if_exists="replace",
    index=False
)

print("Customers Loaded")

products = superstore[
[
    "Product ID",
    "Product Name",
    "Category",
    "Sub-Category"
]]

products = products.drop_duplicates(
    subset=["Product ID"]
)

products.columns = [
    "product_id",
    "product_name",
    "category",
    "sub_category"
]
products.to_sql(
    "products",
    con=engine,
    if_exists="replace",
    index=False
)

print("Products Loaded")

orders = superstore[
[
    "Order ID",
    "Customer ID",
    "Product ID",
    "Order Date",
    "Ship Date",
    "Sales",
    "Quantity",
    "Discount",
    "Profit"
]]

orders.columns = [
    "order_id",
    "customer_id",
    "product_id",
    "order_date",
    "ship_date",
    "sales",
    "quantity",
    "discount",
    "profit"
]
orders.to_sql(
    "orders",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=5000
)

print("Orders Loaded")


# --------------------------------------------------
# INVENTORY
# --------------------------------------------------

inventory = pd.read_csv(
    ROOT_DIR /
    "data" /
    "external" /
    "inventory_data.csv"
)

inventory.to_sql(
    "inventory",
    con=engine,
    if_exists="replace",
    index=False
)

print("Inventory Loaded")

# --------------------------------------------------
# COMPETITORS
# --------------------------------------------------

competitors = pd.read_csv(
    ROOT_DIR /
    "data" /
    "external" /
    "competitor_data.csv"
)

competitors.to_sql(
    "competitors",
    con=engine,
    if_exists="replace",
    index=False
)

print("Competitors Loaded")

print("\nDATABASE LOAD COMPLETE")
