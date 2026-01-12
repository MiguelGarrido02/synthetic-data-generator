# Synthetic Banking Data Generator

#### A robust, configurable, and statistically grounded synthetic data generator designed to simulate banking ecosystems. This tool creates realistic **Customer** and **Transaction** datasets, ideal for testing ETL pipelines, validating database schemas, and training Machine Learning models (e.g., Fraud Detection, Churn Prediction) without compromising sensitive real-world data.
---
## Key Features

* **Statistical Realism:**
    * Uses **Log-normal distributions** for transaction amounts to simulate realistic spending behavior.
    * Applies **Poisson distributions** for transaction frequency based on customer income tiers.
* **Complex Business Logic:** Simulates real-world correlations defined in `config.yaml`:
    * **Geographical affinity:** Transaction countries are weighted based on the customer's home region.
    * **Channel Logic:** Payment methods (Chip, Contactless, Manual) are correlated with the channel (Online, In-store).
* **Data Quality First:** Built-in validation module ensures output datasets strictly adhere to defined schemas and constraints before saving.
* **Format Flexibility:** Supports output in **CSV** (for readability) and **Parquet** (for high-performance analytics).
---
## Tech Stack

* **Language:** Python 3.9+
* **Data Manipulation:** Pandas, NumPy
* **Data Generation:** Faker
* **Configuration:** PyYAML
* **Validation:** Custom Schema Validator based on Pandas Types
---
## Configuration & Customization

The core power of this project lies in `config.yaml`. You can control almost every aspect of the simulation without changing a line of code:

```yaml
# Example snippet from config.yaml
transactions:
  income_tiers:
    low_max: 30000
    mid_max: 70000
  business_rules:
    channels:
      by_merchant_category:
        groceries:
          values: ["in-store", "online", "mobile"]
          weights: [0.8, 0.1, 0.1]
```
You can adjust:
* Dataset size (n_rows).
* Income distributions and customer demographics.
* Transaction volumes per income tier.
* Failure rates (declined/reversed transactions).
* Merchant category weights.
---
## Installation and Usage

1. Clone de repository
```bash
git clone [https://github.com/MiguelGarrido02/synthetic-data-generator.git](https://github.com/MiguelGarrido02/synthetic-data-generator.git)
cd synthetic-data-generator
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Run the generator
```bash
python cli.py
```
4. Check the output: Data will be generated in the data/ folder (or the path defined in your config).
---
## Output Schema

### Customers
| Column | Type | Description |
| :--- | :--- | :--- |
| `customer_id` | UUID | Unique identifier for the customer. |
| `income` | Float | Annual income (Normal distribution). |
| `region` | String | Customer domicile (e.g., ES, FR, US). |
| `age` | Int | Customer age (18-75). |
| `signup_date` | Date | Date when the customer joined. |

### Transactions
| Column | Type | Description |
| :--- | :--- | :--- |
| `transaction_id` | UUID | Unique identifier for the transaction. |
| `amount` | Float | Transaction value (Log-normal distribution). |
| `status` | String | Status (completed, declined, reversed, pending). |
| `channel` | String | Channel used (online, in-store, mobile). |
| `merchant_category`| String | Category (groceries, travel, electronics, etc.). |
| `is_international` | Bool | Flag indicating if transaction country differs from customer region. |
---
## Use Case: Machine Learning

This dataset addresses the "Cold Start" problem in Data Science. It provides a labeled, structured, and relational baseline that can be used to:
* Detect Anomalies/Fraud: The logic generates distinct patterns for normal behavior, allowing the injection of anomalies for model training.
* Customer Segmentation: Income tiers and spending categories allow for clustering analysis.
* Predictive Analytics: Historical transaction data serves as a foundation for forecasting spending trends.
---
