import great_expectations as gx
import pandas as pd
import os
import numpy as np

def validate_parquet():
    print("Starting Parquet Validation...")
    context = gx.get_context(mode="file")
    
    # Generate Parquet Data
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    parquet_path = os.path.join(data_dir, "transactions.parquet")
    print(f"Generating Parquet data at: {parquet_path}")
    
    # Create sample data
    df = pd.DataFrame({
        "transaction_id": range(1, 101),
        "amount": np.random.uniform(10, 1000, 100),
        "currency": ["USD"] * 100,
        "timestamp": pd.date_range(start="2023-01-01", periods=100, freq="h")
    })
    
    df.to_parquet(parquet_path, index=False)
    
    # Get or create datasource
    try:
        datasource = context.data_sources.get("my_parquet_datasource")
        print("Using existing datasource")
    except (KeyError, AttributeError):
        try:
            datasource = context.data_sources.add_pandas("my_parquet_datasource")
            print("Created new datasource")
        except AttributeError:
            datasource = context.sources.add_pandas("my_parquet_datasource")
    
    # Get or create asset
    try:
        asset = datasource.get_asset("transactions_asset")
        print("Using existing asset")
    except (KeyError, LookupError):
        batch = datasource.read_parquet(parquet_path, asset_name="transactions_asset")
        print("Created new asset")
        asset = datasource.get_asset("transactions_asset")
    
    # Get or create batch definition
    try:
        batch_def = asset.get_batch_definition("my_batch_def")
        print("Using existing batch definition")
    except (KeyError, LookupError):
        batch_def = asset.add_batch_definition_path("my_batch_def", path=parquet_path)
        print("Created new batch definition")
    
    # Get batch
    batch = batch_def.get_batch()
    
    # Get or create expectation suite
    try:
        suite = context.suites.get("transactions_suite")
        print("Using existing expectation suite")
    except (KeyError, LookupError):
        suite = context.suites.add(gx.ExpectationSuite(name="transactions_suite"))
        print("Created new expectation suite")
    
    validator = context.get_validator(
        batch_list=[batch],
        expectation_suite=suite
    )
    
    # Only add expectations if suite is empty
    if len(suite.expectations) == 0:
        print("Adding expectations...")
        validator.expect_column_values_to_be_between("amount", 0, 10000)
        validator.expect_column_values_to_be_in_set("currency", ["USD", "EUR"])
        validator.expect_column_values_to_not_be_null("timestamp")
        context.suites.add_or_update(validator.expectation_suite)
    else:
        print(f"Suite already has {len(suite.expectations)} expectations")
    
    print("Validating...")
    validation_result = validator.validate()
    
    print("\nValidation Result Summary:")
    print(f"Success: {validation_result.success}")
    
    if validation_result.success:
        print("\nSUCCESS: All expectations met!")
    else:
        print("\nFAILURE: Some expectations failed.")

if __name__ == "__main__":
    validate_parquet()
