# Great Expectations Learning Project

This project contains examples for learning Great Expectations (GX) with persistent Data Docs storage.

## Project Structure

```
DQPracticeGX/
├── .venv/                          # Virtual environment
├── data/                           # Sample data files
│   ├── employees.csv
│   └── transactions.parquet
├── gx/                             # Great Expectations configuration
│   ├── great_expectations.yml      # Main GX config
│   ├── expectations/               # Expectation suites (persisted)
│   ├── validations/                # Validation results (persisted)
│   ├── data_docs/                  # Data Docs HTML (persisted)
│   │   └── local_site/
│   │       └── index.html          # Main Data Docs page
│   ├── checkpoints/                # Checkpoint configurations
│   └── plugins/                    # Custom plugins
├── 01_hello_world.py               # Basic GX example with Data Docs
├── 02_csv_validation.py            # CSV validation example
├── 03_parquet_validation.py        # Parquet validation example
└── requirements.txt                # Python dependencies

```

## Data Docs Configuration

The project is configured to **persist all validation results and Data Docs** in the project directory:

- **Validation Results**: Stored in `gx/validations/`
- **Data Docs**: Stored in `gx/data_docs/local_site/`
- **Expectations**: Stored in `gx/expectations/`

Every time you run a validation script, the results are **appended** to the existing Data Docs, allowing you to track validation history over time.

## Running the Examples

All scripts use a file-based GX context for persistence:

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run examples
python 01_hello_world.py    # Opens Data Docs in browser
python 02_csv_validation.py
python 03_parquet_validation.py
```

## Viewing Data Docs

Data Docs are automatically built and can be viewed at:
- **File Path**: `gx/data_docs/local_site/index.html`
- **Opens automatically** when running `01_hello_world.py`

You can also manually open the HTML file in your browser to view all validation results.

## Key Configuration

The `gx/great_expectations.yml` file has been configured with:

```yaml
# Validation results stored in project (not uncommitted/)
validation_results_store:
  store_backend:
    base_directory: validations/

# Data Docs stored in project (not uncommitted/)
data_docs_sites:
  local_site:
    store_backend:
      base_directory: data_docs/local_site/
```

This ensures all validation history is preserved and committed to version control.
