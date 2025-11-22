import great_expectations as gx
import pandas as pd
import os

def validate_csv():
    print("Starting CSV Validation...")
    context = gx.get_context(mode="file")
    
    csv_path = os.path.join("data", "employees.csv")
    print(f"Reading CSV from: {csv_path}")
    
    # Get or create datasource
    try:
        datasource = context.data_sources.get("my_csv_datasource")
        print("Using existing datasource")
    except (KeyError, AttributeError):
        try:
            datasource = context.data_sources.add_pandas("my_csv_datasource")
            print("Created new datasource")
        except AttributeError:
            datasource = context.sources.add_pandas("my_csv_datasource")
    
    # Get or create asset
    try:
        asset = datasource.get_asset("employees_asset")
        print("Using existing asset")
    except (KeyError, LookupError):
        batch = datasource.read_csv(csv_path, asset_name="employees_asset")
        print("Created new asset")
        asset = datasource.get_asset("employees_asset")
    
    # Get or create batch definition
    try:
        batch_def = asset.get_batch_definition("my_batch_def")
        print("Using existing batch definition")
    except (KeyError, LookupError):
        batch_def = asset.add_batch_definition_path("my_batch_def", path=csv_path)
        print("Created new batch definition")
    
    # Get batch
    batch = batch_def.get_batch()
    
    # Get or create expectation suite
    try:
        suite = context.suites.get("employees_suite")
        print("Using existing expectation suite")
    except (KeyError, LookupError):
        suite = context.suites.add(gx.ExpectationSuite(name="employees_suite"))
        print("Created new expectation suite")
    
    validator = context.get_validator(
        batch_list=[batch],
        expectation_suite=suite
    )
    
    # Only add expectations if suite is empty
    if len(suite.expectations) == 0:
        print("Adding expectations...")
        validator.expect_column_values_to_be_unique("id")
        validator.expect_column_values_to_be_in_set("department", ["Engineering", "Marketing", "HR", "Sales"])
        validator.expect_column_values_to_be_between("salary", 0, 200000)
        validator.expect_column_values_to_not_be_null("name")
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
        for result in validation_result.results:
            if not result.success:
                print(f"Failed Expectation: {result.expectation_config.expectation_type}")
                print(f"Result: {result.result}")

if __name__ == "__main__":
    validate_csv()
