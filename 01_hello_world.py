import great_expectations as gx
import pandas as pd
from great_expectations.data_context.types.resource_identifiers import ValidationResultIdentifier, ExpectationSuiteIdentifier
from great_expectations.core.run_identifier import RunIdentifier
import datetime

def hello_world():
    print("Starting Hello World GX...")
    context = gx.get_context(mode="file")
    
    data = {
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35]
    }
    df = pd.DataFrame(data)
    
    # Get or create datasource
    try:
        datasource = context.data_sources.get("my_pandas_datasource")
        print("Using existing datasource")
    except (KeyError, AttributeError):
        try:
            datasource = context.data_sources.add_pandas("my_pandas_datasource")
            print("Created new datasource")
        except AttributeError:
            datasource = context.sources.add_pandas("my_pandas_datasource")
    
    # Get or create asset
    try:
        asset = datasource.get_asset("my_df_asset")
        print("Using existing asset")
    except (KeyError, LookupError):
        batch = datasource.read_dataframe(df, asset_name="my_df_asset")
        print("Created new asset")
        asset = datasource.get_asset("my_df_asset")
    
    # Get or create batch definition
    try:
        batch_def = asset.get_batch_definition("my_batch_def")
        print("Using existing batch definition")
    except (KeyError, LookupError):
        batch_def = asset.add_batch_definition_whole_dataframe("my_batch_def")
        print("Created new batch definition")
    
    # Get batch from definition
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})
    
    # Get or create expectation suite
    try:
        suite = context.suites.get("my_hello_world_suite")
        print("Using existing expectation suite")
    except (KeyError, LookupError):
        suite = context.suites.add(gx.ExpectationSuite(name="my_hello_world_suite"))
        print("Created new expectation suite")
    
    # Create validator with existing suite
    validator = context.get_validator(
        batch_list=[batch],
        expectation_suite=suite
    )
    
    # Only add expectations if suite is empty
    if len(suite.expectations) == 0:
        print("Adding expectations to new suite...")
        validator.expect_column_values_to_not_be_null("name")
        validator.expect_column_values_to_be_between("age", 20, 40)
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
        
    print("Generating Data Docs...")
    
    # Manually add validation result to the store
    run_id = RunIdentifier(run_name="my_run", run_time=datetime.datetime.now(datetime.timezone.utc))
    suite_identifier = ExpectationSuiteIdentifier("my_hello_world_suite")
    
    identifier = ValidationResultIdentifier(
        expectation_suite_identifier=suite_identifier,
        run_id=run_id,
        batch_identifier="my_batch"
    )
    
    context.validation_results_store.add(key=identifier, value=validation_result)
    
    print("Building and opening Data Docs...")
    context.build_data_docs()
    context.open_data_docs()

if __name__ == "__main__":
    hello_world()
