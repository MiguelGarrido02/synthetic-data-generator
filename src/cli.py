from src.generators.customers import generate_customers
from src.config_loader import load_config
from src.generators.customers import generate_customers
from src.validation.validator import validate_customer_df
from pathlib import Path
from src.generators.transactions import generate_transactions
from src.validation.validator import validate_transaction_df

def main():
    print("Starting process...\n____________________________")

    cfg = load_config() # Load configuration
    
    if cfg["datasets"]["customers"]["enabled"]:
        print("Generating customers dataset...")
        customers_df = generate_customers(cfg)

        print("Validating customers dataset...")
        if validate_customer_df(customers_df):
            print("Customers dataset is valid.")
        else:
            print("Customers dataset is invalid.")
            print("Process terminated due to validation failure.")
            return
        
        output_path = cfg["datasets"]["customers"]["output"]["path"] # get path from config
        # create parent directories if they don't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if cfg["datasets"]["customers"]["output"]["format"] == "csv":
            print("Saving customers dataset to CSV...")
            customers_df.to_csv(output_path, index=False)
            print(f"Customers dataset saved to {output_path} in CSV format.")
        elif cfg["datasets"]["customers"]["output"]["format"] == "parquet":
            print("Saving customers dataset to Parquet...")
            customers_df.to_parquet(output_path, index=False)
            print(f"Customers dataset saved to {output_path} in Parquet format.")
        else:
            print("Unsupported output format specified in configuration.")

    if cfg["datasets"]["transactions"]["enabled"]:
        print("Generating transactions dataset...")


        transactions_df = generate_transactions(cfg, customers_df)

        print("Validating transactions dataset...")
        if validate_transaction_df(transactions_df):
            print("Transactions dataset is valid.")
        else:
            print("Transactions dataset is invalid.")
            print("Process terminated due to validation failure.")
            return
        
        output_path = cfg["datasets"]["transactions"]["output"]["path"] # get path from config
        # create parent directories if they don't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if cfg["datasets"]["transactions"]["output"]["format"] == "csv":
            print("Saving transactions dataset to CSV...")
            transactions_df.to_csv(output_path, index=False)
            print(f"Transactions dataset saved to {output_path} in CSV format.")
        elif cfg["datasets"]["transactions"]["output"]["format"] == "parquet":
            print("Saving transactions dataset to Parquet...")
            transactions_df.to_parquet(output_path, index=False)
            print(f"Transactions dataset saved to {output_path} in Parquet format.")
        else:
            print("Unsupported output format specified in configuration.")

        

        

if __name__ == "__main__":
    main()