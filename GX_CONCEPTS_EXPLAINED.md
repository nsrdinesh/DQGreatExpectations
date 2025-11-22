 # Great Expectations Concepts Explained

## Overview

Great Expectations (GX) is a Python library for **data quality validation**. It helps you define what you expect from your data and automatically validates those expectations, providing detailed reports.

---

## Core Concepts

### 1. Data Context

The **Data Context** is the central configuration object in GX. It manages all your datasources, expectation suites, validation results, and Data Docs.

```python
context = gx.get_context(mode="file")
```

**Two modes:**
- **Ephemeral mode** (default): Everything stored in memory, lost when script ends
- **File mode**: Persists configuration and results to disk in the `gx/` directory

**What it stores:**
- Datasource configurations
- Expectation suites (your validation rules)
- Validation results (history of checks)
- Data Docs configuration

---

### 2. Datasource

A **Datasource** tells GX where your data lives and how to access it.

```python
datasource = context.data_sources.add_pandas("my_pandas_datasource")
```

**Types:**
- **Pandas**: For CSV, Excel, Parquet, in-memory DataFrames
- **SQL**: For databases (PostgreSQL, MySQL, etc.)
- **Spark**: For big data processing

**Why it persists:** In file mode, datasource configurations are saved so you don't recreate them every time.

---

### 3. Data Asset

A **Data Asset** represents a specific dataset within a datasource (e.g., a CSV file, a database table, or a DataFrame).

```python
asset = datasource.get_asset("my_df_asset")
```

**Examples:**
- CSV file: `employees.csv`
- Database table: `users` table
- Parquet file: `transactions.parquet`

**Key point:** Assets are reusable - once defined, you can get batches from them repeatedly.

---

### 4. Batch

A **Batch** is a specific snapshot of data from an asset at a point in time.

```python
batch = batch_def.get_batch(batch_parameters={"dataframe": df})
```

**Why batches?**
- Your data changes over time
- Each validation run gets a fresh batch
- Allows tracking data quality trends

**Batch Definition:** Defines HOW to get a batch (e.g., "read this CSV file" or "query this table")

---

### 5. Expectation

An **Expectation** is a single, verifiable assertion about your data.

```python
validator.expect_column_values_to_not_be_null("name")
validator.expect_column_values_to_be_between("age", 20, 40)
```

**Common expectations:**
- `expect_column_values_to_not_be_null`: No missing values
- `expect_column_values_to_be_unique`: No duplicates
- `expect_column_values_to_be_between`: Values in range
- `expect_column_values_to_be_in_set`: Values from allowed list
- `expect_table_row_count_to_be_between`: Row count validation

**100+ built-in expectations** available!

---

### 6. Expectation Suite

An **Expectation Suite** is a collection of expectations that define what "good data" looks like for a dataset.

```python
suite = context.suites.add(gx.ExpectationSuite(name="my_hello_world_suite"))
```

**Think of it as:**
- A test suite for your data
- A contract defining data quality standards
- Reusable validation rules

**Why check if empty?** In file mode, suites persist. We only add expectations once to avoid duplicates.

---

### 7. Validator

A **Validator** combines a batch of data with an expectation suite to run validations.

```python
validator = context.get_validator(
    batch_list=[batch],
    expectation_suite=suite
)
```

**What it does:**
- Applies expectations to actual data
- Returns validation results (pass/fail)
- Can add new expectations interactively

---

### 8. Validation Result

The **Validation Result** contains the outcome of running expectations against data.

```python
validation_result = validator.validate()
print(f"Success: {validation_result.success}")  # True or False
```

**Contains:**
- Overall success/failure
- Individual expectation results
- Statistics (how many passed/failed)
- Detailed metrics for each check

---

### 9. Data Docs

**Data Docs** are automatically generated HTML reports that visualize your validation results.

```python
context.build_data_docs()
context.open_data_docs()
```

**What you see:**
- Interactive dashboards
- Expectation suite documentation
- Validation history and trends
- Pass/fail statistics with charts

**Location:** `gx/data_docs/local_site/index.html`

---

## Hello World Code Walkthrough

Let's break down the `01_hello_world.py` script step by step:

### Step 1: Initialize Context

```python
context = gx.get_context(mode="file")
```

Creates a file-based context that persists everything to the `gx/` directory.

---

### Step 2: Create Sample Data

```python
data = {
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35]
}
df = pd.DataFrame(data)
```

Simple in-memory DataFrame for demonstration.

---

### Step 3: Get or Create Datasource

```python
try:
    datasource = context.data_sources.get("my_pandas_datasource")
    print("Using existing datasource")
except (KeyError, AttributeError):
    datasource = context.data_sources.add_pandas("my_pandas_datasource")
    print("Created new datasource")
```

**Why try/except?** 
- First run: Creates datasource
- Subsequent runs: Reuses existing datasource
- Avoids "already exists" errors

---

### Step 4: Get or Create Asset

```python
try:
    asset = datasource.get_asset("my_df_asset")
except (KeyError, LookupError):
    batch = datasource.read_dataframe(df, asset_name="my_df_asset")
    asset = datasource.get_asset("my_df_asset")
```

**What happens:**
- First run: `read_dataframe` creates the asset
- Subsequent runs: Gets existing asset definition

---

### Step 5: Get or Create Batch Definition

```python
try:
    batch_def = asset.get_batch_definition("my_batch_def")
except (KeyError, LookupError):
    batch_def = asset.add_batch_definition_whole_dataframe("my_batch_def")
```

**Batch Definition types:**
- `add_batch_definition_whole_dataframe`: For in-memory DataFrames
- `add_batch_definition_path`: For files (CSV, Parquet)
- `add_batch_definition_query`: For SQL queries

---

### Step 6: Get Fresh Batch

```python
batch = batch_def.get_batch(batch_parameters={"dataframe": df})
```

**Key insight:** Even though the definition is reused, we get a FRESH batch with current data each time.

---

### Step 7: Get or Create Expectation Suite

```python
try:
    suite = context.suites.get("my_hello_world_suite")
except (KeyError, LookupError):
    suite = context.suites.add(gx.ExpectationSuite(name="my_hello_world_suite"))
```

Reuses suite if it exists, creates new one if not.

---

### Step 8: Create Validator

```python
validator = context.get_validator(
    batch_list=[batch],
    expectation_suite=suite
)
```

Connects the data (batch) with the rules (suite).

---

### Step 9: Add Expectations (First Run Only)

```python
if len(suite.expectations) == 0:
    validator.expect_column_values_to_not_be_null("name")
    validator.expect_column_values_to_be_between("age", 20, 40)
    context.suites.add_or_update(validator.expectation_suite)
```

**Why check if empty?**
- First run: Suite is empty, add expectations
- Subsequent runs: Suite already has expectations, skip

---

### Step 10: Validate

```python
validation_result = validator.validate()
print(f"Success: {validation_result.success}")
```

Runs all expectations against the data and returns results.

---

### Step 11: Store Results & Build Data Docs

```python
run_id = RunIdentifier(run_name="my_run", run_time=datetime.datetime.now(datetime.timezone.utc))
suite_identifier = ExpectationSuiteIdentifier("my_hello_world_suite")

identifier = ValidationResultIdentifier(
    expectation_suite_identifier=suite_identifier,
    run_id=run_id,
    batch_identifier="my_batch"
)

context.validation_results_store.add(key=identifier, value=validation_result)
context.build_data_docs()
context.open_data_docs()
```

**What happens:**
1. Creates unique identifier for this validation run
2. Stores result in `gx/validations/`
3. Rebuilds Data Docs HTML with new results
4. Opens Data Docs in browser

---

## Key Patterns in File-Based Context

### Pattern: Get or Create

```python
try:
    obj = context.get_thing("name")
    print("Using existing")
except (KeyError, LookupError):
    obj = context.add_thing("name")
    print("Created new")
```

**Why?** File mode persists objects. This pattern prevents "already exists" errors on subsequent runs.

### Pattern: Conditional Expectations

```python
if len(suite.expectations) == 0:
    # Add expectations
```

**Why?** Expectations persist in file mode. Only add them once.

### Pattern: Fresh Batches

```python
batch = batch_def.get_batch(batch_parameters={"dataframe": df})
```

**Why?** Even with persisted definitions, we get fresh data each run.

---

## Data Quality Workflow

1. **Define** expectations (what good data looks like)
2. **Validate** data against expectations
3. **Review** results in Data Docs
4. **Track** trends over time
5. **Alert** on failures (can integrate with CI/CD)

---

## Benefits of Great Expectations

✅ **Automated validation** - No manual data checks  
✅ **Documentation** - Expectations serve as data contracts  
✅ **Visibility** - Beautiful HTML reports  
✅ **Version control** - Expectations stored as code  
✅ **Collaboration** - Share Data Docs with team  
✅ **CI/CD integration** - Fail builds on bad data  
✅ **Trend tracking** - Historical validation results  

---

## Common Use Cases

1. **ETL Pipeline Validation**: Validate data after each transformation
2. **Data Ingestion**: Check incoming data quality
3. **ML Pipeline**: Validate training/inference data
4. **Database Migration**: Ensure data integrity
5. **API Response Validation**: Check external data sources
6. **Reporting**: Validate data before generating reports

---

## Next Steps

- **Task 2**: CSV validation with file-based data
- **Task 3**: Parquet validation for big data
- **Task 4**: Database validation with Supabase
- **Task 5**: Custom expectations for complex rules
- **Task 6**: Explore 100+ built-in expectations
