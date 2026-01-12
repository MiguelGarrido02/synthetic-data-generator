# This generates the customers synthetic data

# We want to generate data for customers including their id, name, region, age, income, and signup date.

import pandas as pd
import uuid
from faker import Faker
fake = Faker("es_ES")
import numpy as np

def generate_customers(cfg: dict) -> pd.DataFrame:
    """Generate synthetic customer data based on configuration parameters."""

    # Read configuration parameters
    customers_cfg = cfg["datasets"]["customers"]
    n_customers = customers_cfg["n_rows"]

    min_age = customers_cfg["age"]["min"]
    max_age = customers_cfg["age"]["max"]

    mean_income = customers_cfg["income"]["mean"]
    stddev_income = customers_cfg["income"]["stddev"]

    start_date = customers_cfg["signup_date"]["start"]
    end_date = customers_cfg["signup_date"]["end"]

    regions = customers_cfg["region"]["values"]
    weights = customers_cfg["region"]["weights"]

    # Combine all generated data into a DataFrame
    data = {
        "customer_id": generate_customer_ids(n_customers),
        "customer_name": generate_customer_names(n_customers),
        "age": generate_customer_ages(n_customers, min_age, max_age),
        "income": generate_customer_incomes(n_customers, mean_income, stddev_income),
        "signup_date": generate_customer_signup_dates(n_customers, start_date, end_date),
        "region": generate_customer_regions(n_customers, regions, weights)
    }

    customers_df = pd.DataFrame(data)
    #print(customers_df.head())  # Test: Print first few rows of the generated DataFrame
    return customers_df

def generate_customer_ids(n: int) -> list:
    """Generate a list of unique customer IDs according to the number of rows in the config."""
    uuids_list = [str(uuid.uuid4()) for _ in range(n)]
    # print(uuids_list) #test
    return uuids_list

def generate_customer_names(n: int) -> list:
    """Generate a list of customer names"""
    names_list = [fake.name() for _ in range(n)]
    # print(names_list) #test
    return names_list

def generate_customer_ages(n:int, min_age: int, max_age: int) -> list:
    """Generate a list of customer ages, following normal distribution"""
    """Centre of the distribution is the mean of min_age and max_age, with a standard deviation of 20"""
    """ Ages out of range are clipped to the min and max values"""
    ages_array = np.random.normal(loc=(min_age + max_age)/2, scale = 15, size=n) 
    ages_array = np.clip(ages_array, min_age, max_age).astype(int)
    ages_list = ages_array.tolist()
    # print(ages_list) #test
    return ages_list

def generate_customer_incomes(n:int, mean: float, stddev: float) -> list:
    """Generate a list of customer incomes, following normal distribution, only clipping negative values to zero"""
    incomes_array = np.random.normal(loc=mean, scale = stddev, size = n)
    incomes_array = np.clip(incomes_array, 0, None)
    incomes_list = incomes_array.tolist()
    # set incomes below 15000 to 15000
    incomes_list = [income if income >= 15000 else 15000 for income in incomes_list]
    # print(incomes_list) #test
    return incomes_list

def generate_customer_signup_dates(n:int, start_date: str, end_date: str) -> list:
    """Generate a list of customer random signup dates between start_date and end_date"""
    start_u = pd.to_datetime(start_date).value // 10**9 # Convert to unix timestamp in seconds
    end_u = pd.to_datetime(end_date).value // 10**9 # Convert to unix timestamp in seconds
    random_unix_dates = np.random.randint(start_u, end_u, n)
    signup_dates = pd.to_datetime(random_unix_dates, unit='s').tolist() # Convert back to datetime format and list everything
    # print(signup_dates) #test
    return signup_dates

def generate_customer_regions(n:int, regions: list, weights: list) -> list:
    """Generate a list of customer regions based on given regions and their weights"""
    regions_list = np.random.choice(regions, size = n, p = weights).tolist()
    #print(regions_list) #test
    return regions_list


# Testing
# if __name__ == "__main__":
#     from src.config_loader import load_config
#     cfg = load_config()
#     generate_customers(cfg)


