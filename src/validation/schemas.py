"""Schemas defining the expected structure and constraints for each dataset.
These schemas DO NOT perform validation. They only declare rules.
Validation logic lives in validator.py."""

class CustomerSchema:
    """Schema for the 'customers' dataset."""
    # Columns that must be present in the dataset
    required_columns = ['customer_id', 'customer_name', 'age', 'income', 'signup_date', 'region']

    # Expected data types for each column
    # Note: These are semantic types; validator.py will map them to actual pandas dtypes.
    dtypes = {
        'customer_id': str,
        'customer_name': str,
        'age': int,
        'income': float,
        'signup_date': 'datetime64[ns]',
        'region': str
    }

    # Constraints for each column
    constraints = {
        'age': {
            'min': 18,
            'max': 75
        },
        'income': {
            'min': 0.0
        },
        'signup_date': {
            'min': '2020-01-01',
            'max': '2023-01-01'
        },
        'region': {
            'allowed_values': ['ES', 'FR', 'DE', 'US', 'CN']
        }
    }


class TransactionSchema:
    """Schema for the 'transactions' dataset."""

    # Required columns
    required_columns = [
        "transaction_id",
        "customer_id",
        "transaction_timestamp",
        "transaction_amount",
        "merchant_category",
        "transaction_status",
        "entry_mode",
        "channel",
        "transaction_country",
        "is_international",
    ]

    # 2) Expected data types (semantic)
    dtypes = {
        "transaction_id": str,
        "customer_id": str,
        "transaction_timestamp": "datetime64[ns]",
        "transaction_amount": float,
        "merchant_category": str,
        "transaction_status": str,
    }

    # 3) Basic business constraints
    # NOTE: put dates here that match your config.yaml
    # datasets.transactions.date_range.start / end
    constraints = {
        "transaction_amount": {
            "min": 0.0,          # never negative amounts
            # "max": 1_000_000.0  # optional upper limit
        },
        "transaction_timestamp": {
            "min": "2020-01-01",  # adjust to match config.yaml!
            "max": "2023-01-01",
        },
        "merchant_category": {
            "allowed_values": [
                "groceries",
                "electronics",
                "clothing",
                "restaurants",
                "utilities",
                "travel",
                "entertainment",
                "health",
                "education",
                "others",
            ],
        },
        "transaction_status": {
            "allowed_values": [
                "completed",
                "declined",
                "reversed",
                "pending",
            ],
        },
        "entry_mode": {
            "allowed_values": [
                "swiped",
                "chip",
                "contactless",
                "manual",
            ],
        },
        "channels": {
            "allowed_values": [
                "online",
                "in-store",
                "mobil",
            ],
        },
        "transaction_country": {
            "allowed_values": [
                "ES",
                "FR",
                "DE",
                "US",
                "CN",
                "MX",
                "CA",
            ],
        },

    }
