# This generates the transactions synthetic data
# All transactions will be generated for existing customers with existing IDs, one customer can have multiple transactions.

import pandas as pd
import numpy as np
import uuid

def generate_transactions(cfg: dict, customers_df: pd.DataFrame) -> pd.DataFrame:
    """Generate synthetic transactions data based on configuration parameters and existing customers."""

    # Load transactions configuration
    transactions_cfg = cfg["datasets"]["transactions"]
    customers_df = assign_income_tier(customers_df, cfg["datasets"]["transactions"]["income_tiers"])
    customers_df = compute_active_period(customers_df, 
                                        pd.Timestamp(cfg["datasets"]["transactions"]["date_range"]["start"]),
                                        pd.Timestamp(cfg["datasets"]["transactions"]["date_range"]["end"]))
    customers_df = generate_num_transactions_per_customer(customers_df, transactions_cfg)
    transactions_df = expand_customers_to_transactions(customers_df)
    transactions_df = generate_transaction_dates(transactions_df)
    transactions_df = generate_transactions_amounts(transactions_df, transactions_cfg)
    transactions_df = generate_merchant_categories(transactions_df, 
                                                   transactions_cfg["categories"]["merchant_categories"],
                                                    transactions_cfg["categories"]["weights"])
    transactions_df = generate_transaction_statuses(transactions_df,
                                                    transactions_cfg["status_distribution"]["values"],
                                                    transactions_cfg["status_distribution"]["weights"])
    transactions_df = generate_transaction_ids(transactions_df)
    transactions_df = generate_transaction_channels(transactions_df,
                                                    transactions_cfg["business_rules"]["channels"])
    transactions_df = generate_entry_modes(transactions_df,
                                           transactions_cfg["business_rules"]["entry_modes"])
    transactions_df = generate_transaction_country(transactions_df,
                          transactions_cfg["business_rules"]["transaction_country"])
    transactions_df = derive_is_international(transactions_df)

    transactions_df = df_cleanup(transactions_df)
    # print("___________________________")
    # print(transactions_df.head())  # Test: Print first few rows after adding transaction info
    #print column names
    # print(transactions_df.columns.tolist())

    return transactions_df

def assign_income_tier(customers_df: pd.DataFrame, income_tiers_cfg: dict) -> pd.DataFrame:
    """Assign income tier to each customer based on their anual income"""

    income_tiers = []
    for income in customers_df["income"]:
        if income < income_tiers_cfg["low_max"]:
            income_tiers.append("low")
        elif income < income_tiers_cfg["mid_max"]:
            income_tiers.append("mid")
        else:
            income_tiers.append("high")
    
    customers_df["income_tier"] = income_tiers
    return customers_df


def compute_active_period(customers_df: pd.DataFrame, global_start: pd.Timestamp, global_end: pd.Timestamp) -> pd.DataFrame:
    """Compute active_start, active_end, and active_months for each customer."""

    active_starts = []
    active_ends = []
    active_months_list = []

    for signup_date in customers_df["signup_date"]:
        active_start = max(signup_date, global_start)
        active_end = global_end

        # Months active
        months_active = (active_end.year - active_start.year) * 12 + (active_end.month - active_start.month)
        months_active = max(months_active, 0)

        # Append
        active_starts.append(active_start)
        active_ends.append(active_end)
        active_months_list.append(months_active)

    # Add columns
    customers_df["active_start"] = active_starts
    customers_df["active_end"] = active_ends
    customers_df["active_months"] = active_months_list

    return customers_df



def generate_num_transactions_per_customer(customers_df: pd.DataFrame, transactions_cfg: dict) -> pd.DataFrame:
    """Generate number of transactions per customer based on their income tier and configuration parameters using Poisson distribution."""
    num_transactions_list = []
    for _, row in customers_df.iterrows():
        income_tier = row["income_tier"]
        active_months = row["active_months"]

        if income_tier == "low":
            mean_tx_per_month = transactions_cfg["customer_activity"]["low_income_mean_tx_per_month"]
        elif income_tier == "mid":
            mean_tx_per_month = transactions_cfg["customer_activity"]["mid_income_mean_tx_per_month"]
        else:  # high income tier
            mean_tx_per_month = transactions_cfg["customer_activity"]["high_income_mean_tx_per_month"]

        # Total mean transactions for the active period
        total_mean_tx = mean_tx_per_month * active_months
        num_transactions = np.random.poisson(lam=total_mean_tx)
        num_transactions_list.append(num_transactions)
    
    customers_df["num_transactions"] = num_transactions_list
    return customers_df

def expand_customers_to_transactions(customers_df: pd.DataFrame) -> pd.DataFrame:
    """Expand customers DataFrame to transactions DataFrame based on num_transactions per customer."""
    transactions_df = customers_df.loc[customers_df.index.repeat(customers_df['num_transactions'])].copy()
    transactions_df.reset_index(drop=True, inplace=True)
    return transactions_df

def generate_transaction_dates(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Generate a random timestamp (date + time) for each transaction between active_start and active_end."""
    
    # Convert datetime to int64 ns for fast operations
    start_ns = transactions_df["active_start"].view("int64")
    end_ns = transactions_df["active_end"].view("int64")
    
    # Range in ns
    delta_ns = end_ns - start_ns

    # Random fraction [0,1) per row
    rand = np.random.rand(len(transactions_df))

    # Compute final timestamps
    random_ns = start_ns + (delta_ns * rand).astype("int64")

    transactions_df["transaction_timestamp"] = pd.to_datetime(random_ns)

    return transactions_df

def generate_transactions_amounts(transactions_df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Generate transactions amounts based on customer's income tier, income amount, and configuration parameters with log-normal distribution."""
    sigma = cfg["amount"]["base_log_normal_sigma"]
    low_factor = cfg["amount"]["low_income_factor"]
    mid_factor = cfg["amount"]["mid_income_factor"]
    high_factor = cfg["amount"]["high_income_factor"]
    
    base_spend = []

    for _, row in transactions_df.iterrows():
        income_tier = row["income_tier"]
        income_annual = row["income"]

        if income_tier == "low":
            factor = low_factor
        elif income_tier == "mid":
            factor = mid_factor
        else:  # high income tier
            factor = high_factor

        monthly_spend = income_annual * factor / 12
        base_spend.append(monthly_spend)

    base_spend = np.array(base_spend)
    # Calculate mu for log-normal distribution
    mu = np.log(base_spend) - (sigma**2) / 2

    # Generate amounts
    amounts = np.random.lognormal(mean=mu, sigma=sigma)

    # Minimum 1€
    amounts = np.clip(amounts, 1.0, None)

    # Maximum 5 times the monthly spend
    max_amounts = base_spend * 5
    amounts = np.minimum(amounts, max_amounts)

    # Round amounts to 2 decimal places
    amounts = np.round(amounts, 2)

    # If amount is zero (should not happen due to clipping), set to 1.0
    
    transactions_df["transaction_amount"] = amounts
    return transactions_df


def generate_merchant_categories(transactions_df: pd.DataFrame, categories: list, weights: list) -> pd.DataFrame:
    """Assign a merchant category to each transaction based on defined categories and weights."""
    merchant_categories = np.random.choice(categories, size=len(transactions_df), p=weights)
    transactions_df["merchant_category"] = merchant_categories
    return transactions_df

def generate_transaction_statuses(transactions_df: pd.DataFrame, statuses: list, weights: list) -> pd.DataFrame:
    """Assign a transaction status to each transaction based on defined statuses and weights."""
    transaction_statuses = np.random.choice(statuses, size=len(transactions_df), p=weights)
    transactions_df["transaction_status"] = transaction_statuses
    return transactions_df

def generate_transaction_ids(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Generate unique transaction IDs for each transaction."""
    transaction_ids = [str(uuid.uuid4()) for _ in range(len(transactions_df))]
    transactions_df["transaction_id"] = transaction_ids
    return transactions_df

def generate_transaction_channels(transactions_df: pd.DataFrame, channels: dict) -> pd.DataFrame:
    """Assign a transaction channel to each transaction based on the merchant category and defined weights for each category."""
    transaction_channels = []
    for _, row in transactions_df.iterrows():
        merchant_category = row["merchant_category"]
        if merchant_category in channels["by_merchant_category"]:
            channel = np.random.choice(channels["by_merchant_category"][merchant_category]["values"], 
                                       p=channels["by_merchant_category"][merchant_category]["weights"])
        else:
            channel = np.random.choice(channels["default_distribution"]["values"], 
                                       p=channels["default_distribution"]["weights"])
        transaction_channels.append(channel)
    transactions_df["channel"] = transaction_channels
    return transactions_df


def generate_entry_modes(transactions_df: pd.DataFrame, entry_modes: dict) -> pd.DataFrame:
    """Assign an entry mode to each transaction based on defined entry modes dependant on the cannel and weights."""
    transaction_entry_modes = []
    for _, row in transactions_df.iterrows():
        channel = row["channel"]
        if channel in entry_modes["by_channel"]:
            entry_mode = np.random.choice(entry_modes["by_channel"][channel]["values"], 
                                       p=entry_modes["by_channel"][channel]["weights"])
        else:
            entry_mode = np.random.choice(entry_modes["default_distribution"]["values"], 
                                       p=entry_modes["default_distribution"]["weights"])
        transaction_entry_modes.append(entry_mode)
    transactions_df["entry_mode"] = transaction_entry_modes
    return transactions_df

def generate_transaction_country(transactions_df: pd.DataFrame, transaction_country_cfg: dict) -> pd.DataFrame:
    """
    Assign a transaction_country to each transaction based on the customer's region
    and the configured domestic/international distributions.
    """

    domestic_probs = transaction_country_cfg.get("domestic_probability_by_region", {})
    international_dests_by_region = transaction_country_cfg.get("international_destinations_by_region", {})
    default_international_dests = transaction_country_cfg.get("default_international_destinations", {})

    transaction_countries = []

    for _, row in transactions_df.iterrows():
        customer_region = row["region"]

        # Domestic transaction prob
        domestic_prob = domestic_probs.get(customer_region, 1.0)  # si no está, asumimos 100% doméstico
        rand = np.random.rand()

        if rand < domestic_prob:
            # Domestic transaction: country = customer region
            tx_country = customer_region
        else:
            # International transaction: choose destination based on region-specific or default config
            dest_cfg = international_dests_by_region.get(customer_region, default_international_dests)

            dest_values = dest_cfg["values"]
            dest_weights = dest_cfg["weights"]

            tx_country = np.random.choice(dest_values, p=dest_weights)

        transaction_countries.append(tx_country)

    transactions_df["transaction_country"] = transaction_countries
    return transactions_df


def derive_is_international(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive is_international flag as a simple comparison between
    transaction_country and customer region.
    """
    transactions_df["is_international"] = transactions_df["transaction_country"] != transactions_df["region"]
    return transactions_df


def df_cleanup(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Remove helper columns used during generation."""
    """Make sure to keep only relevant transaction columns."""
    """Maintain consistency with the expected schema, if columns or columns names are modified, update schema accordingly."""
    columns_to_drop = ["income_tier", "active_start", "active_end", "active_months", "num_transactions", "customer_name",
                       "age", "income", "signup_date", "region"]
    transactions_df = transactions_df.drop(columns=columns_to_drop)
    return transactions_df

# Testing
if __name__ == "__main__":
    from src.config_loader import load_config
    from src.generators.customers import generate_customers
    cfg = load_config()
    df_custom = generate_customers(cfg)
    generate_transactions(cfg, df_custom)