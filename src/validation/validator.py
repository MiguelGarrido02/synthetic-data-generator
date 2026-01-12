from pandas.api.types import (
    is_integer_dtype,
    is_float_dtype,
    is_string_dtype,
    is_datetime64_any_dtype,
)
import pandas as pd
from src.validation import schemas

def validate_customer_df(df: pd.DataFrame) -> bool:
    """Validate the customers DataFrame against the CustomerSchema."""
    is_valid = True

    # Check required columns
    if not check_required_columns(df, schemas.CustomerSchema.required_columns):
        is_valid = False

    # Check data types
    if not check_column_dtypes(df, schemas.CustomerSchema.dtypes):
        is_valid = False

    # Check constraints
    if not check_column_constraints(df, schemas.CustomerSchema.constraints):
        is_valid = False

    return is_valid

def validate_transaction_df(df: pd.DataFrame) -> bool:
    """Validate the transactions DataFrame against the TransactionSchema."""
    is_valid = True

    # Check required columns
    if not check_required_columns(df, schemas.TransactionSchema.required_columns):
        is_valid = False

    # Check data types
    if not check_column_dtypes(df, schemas.TransactionSchema.dtypes):
        is_valid = False

    # Check constraints
    if not check_column_constraints(df, schemas.TransactionSchema.constraints):
        is_valid = False

    return is_valid


def check_required_columns(df:pd.DataFrame, required_columns: list) -> bool:
    """Check if all required columns are present in the DataFrame."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        return False
    return True

def check_column_dtypes(df: pd.DataFrame, dtypes: dict) -> bool:
    """
    Check if the DataFrame columns have the expected data types
    according to the dtypes defined in the schema.

    In CustomerSchema.dtypes you have a mix of:
      - Python types: str, int, float
      - A string for datetime: 'datetime64[ns]'
    """
    ok = True

    for col, expected_dtype in dtypes.items():
        if col not in df.columns:
            # If the column doesn't exist, that is checked by check_required_columns
            continue

        series = df[col]
        actual_dtype = series.dtype

        # Case 1: Python types
        if expected_dtype is str:
            if not is_string_dtype(series):
                print(
                    f"[VALIDATION] Column '{col}' has dtype '{actual_dtype}', "
                    f"expected a string-like dtype"
                )
                ok = False

        elif expected_dtype is int:
            if not is_integer_dtype(series):
                print(
                    f"[VALIDATION] Column '{col}' has dtype '{actual_dtype}', "
                    f"expected an integer dtype"
                )
                ok = False

        elif expected_dtype is float:
            if not is_float_dtype(series):
                print(
                    f"[VALIDATION] Column '{col}' has dtype '{actual_dtype}', "
                    f"expected a float dtype"
                )
                ok = False

        # Case 2: String types for special dtypes
        elif isinstance(expected_dtype, str) and expected_dtype.startswith("datetime"):
            if not is_datetime64_any_dtype(series):
                print(
                    f"[VALIDATION] Column '{col}' has dtype '{actual_dtype}', "
                    f"expected a datetime dtype (e.g. datetime64[ns])"
                )
                ok = False

        else:
            # Non expected dtype
            print(
                f"[VALIDATION] No type checker implemented for expected dtype "
                f"'{expected_dtype}' in column '{col}'"
            )
            ok = False

    return ok

def check_column_constraints(df: pd.DataFrame, constraints: dict) -> bool:
    """Check if the DataFrame columns meet the defined constraints."""
    ok = True

    for col, rules in constraints.items():
        if col not in df.columns:
            continue

        series = df[col]
        is_dt = is_datetime64_any_dtype(series)

        # MIN
        if "min" in rules:
            min_val = rules["min"]
            if is_dt:
                min_val = pd.to_datetime(min_val)
            if (series < min_val).any():
                print(f"Column '{col}' has values below minimum of {rules['min']}")
                ok = False

        # MAX
        if "max" in rules:
            max_val = rules["max"]
            if is_dt:
                max_val = pd.to_datetime(max_val)
            if (series > max_val).any():
                print(f"Column '{col}' has values above maximum of {rules['max']}")
                ok = False

        # allowed_values
        if "allowed_values" in rules:
            if not series.isin(rules["allowed_values"]).all():
                print(
                    f"Column '{col}' has values outside allowed set: "
                    f"{rules['allowed_values']}"
                )
                ok = False

    return ok


