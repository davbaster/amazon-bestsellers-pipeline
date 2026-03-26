# amazon-bestsellers-analytics-pipeline

This project builds a cloud-ready DataOps pipeline to analyze Amazon bestseller patterns using Bruin, Terraform, and GCP.

## Problem Description

The project solves a simple but realistic analytics problem: turning a flat bestseller CSV into a reproducible cloud pipeline that supports author and genre analysis.

The business questions are:

- which authors appear most often in the bestseller dataset
- what nationality dominates in the dataset
- which genres dominate the dataset overall
- which genres dominate the dataset per year

The pipeline takes local raw files, uploads them to a cloud data lake, loads them into a warehouse, transforms them into analytics tables, and exposes the outputs in a dashboard.

## Demo Data Location

This is a demo course project, so the raw input files are intentionally stored in the repository under [`pipeline/assets/`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/assets).

For each run:

1. the source files start in `pipeline/assets/`
2. they are uploaded to the GCS raw zone
3. they are loaded and transformed in BigQuery

## Quick Start

### Cloud Deployment

#### 1. Prerequisites

- Install Terraform
- Install Bruin CLI
- Install Google Cloud SDK (`gcloud`)
- Install Python dependencies with `pip install -r requirements.txt`
- Create or use an existing GCP project
- Download a GCP service account JSON key and save it as `service-account.json`
- Copy `.bruin.yml.example` to `.bruin.yml` and fill in your GCP values

Enable the required GCP APIs:

```bash
gcloud services enable \
  bigquery.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  storage.googleapis.com
```

Authenticate locally:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account.json"
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
gcloud config set project your-gcp-project-id
```

#### 2. Infrastructure Setup

```bash
export TF_VAR_project_id="your-gcp-project-id"
export TF_VAR_region="us-central1"

cd infrastructure/gcp
terraform init
terraform apply
```

If the bucket already exists and you want Terraform to manage it, import it before `terraform apply`:

```bash
export BUCKET_NAME="${TF_VAR_project_id}-amz-bestsellers-raw"
terraform import google_storage_bucket.data_lake "$BUCKET_NAME"
```

Image placeholder:

![Infrastructure Setup Placeholder](docs/images/step-01-infrastructure-setup.png)

#### 3. Run the Pipeline

```bash
# Setup your Bruin environment
bruin init

# Upload the raw files to the cloud data lake
export RAW_DATA_LAKE_BUCKET=$(terraform -chdir=infrastructure/gcp output -raw data_lake_bucket_name)
make upload-raw

# Run the Bruin batch DAG in BigQuery
make pipeline-cloud
```

Image placeholder:

![Pipeline Run Placeholder](docs/images/step-02-pipeline-run.png)

#### 4. Launch Dashboard

```bash
pip install streamlit
streamlit run dashboard/app.py
```

Image placeholder:

![Dashboard Placeholder](docs/images/step-03-dashboard.png)

### Local Execution (Optional)

If you do not want to use GCP, use the local Docker environment:

```bash
cd infrastructure/local
terraform init
terraform apply
make infra-local
make pipeline
```

The expected cloud workflow is:

1. Provision infrastructure on GCP with Terraform
2. Upload batch files to the GCS raw data lake
3. Run the Bruin DAG to build staging, dimensions, and facts in BigQuery
4. Query the final tables and expose results in the dashboard

## Validation And Smoke Tests

Yes, you can and should use simple tests to confirm the infrastructure and data were created correctly.

### 1. Verify Terraform Outputs

```bash
terraform -chdir=infrastructure/gcp output
```

Expected:

- a raw GCS bucket name
- a `raw` BigQuery dataset
- an `analytics` BigQuery dataset
- a pipeline service account email

### 2. Verify Files Reached The Data Lake

```bash
gcloud storage ls "gs://${RAW_DATA_LAKE_BUCKET}/raw/"
```

Expected files:

- `bestsellers_with_categories.csv`
- `author_nationality_seed.csv`

### 3. Verify BigQuery Datasets Exist

```bash
bq ls --project_id "$TF_VAR_project_id"
```

Expected datasets:

- `raw`
- `analytics`

### 4. Verify The Core Analytical Tables Exist

```bash
bq ls "${TF_VAR_project_id}:analytics"
```

Expected tables:

- `fct_author_appearances`
- `fct_nationality_distribution`
- `fct_genre_overall`
- `fct_genre_by_year`

### 5. Verify Row Counts

```bash
bq query --use_legacy_sql=false \
'SELECT COUNT(*) AS row_count FROM `'"$TF_VAR_project_id"'.analytics.fct_author_appearances`'
```

Expected:

- a non-zero row count

```bash
bq query --use_legacy_sql=false \
'SELECT COUNT(*) AS row_count FROM `'"$TF_VAR_project_id"'.analytics.fct_genre_by_year`'
```

Expected:

- a non-zero row count

### 6. Verify The Dashboard

After launching Streamlit, confirm that the dashboard renders at least:

- the author appearance view
- the nationality distribution view
- the overall genre view
- the yearly genre view

### 7. Run Repo-Level Checks

```bash
make test
python3 -m py_compile \
  dashboard/app.py \
  pipeline/ingestion/enrich_author_nationality.py \
  pipeline/ingestion/upload_to_gcs.py \
  pipeline/assets/ingest_raw_files.py
```

These checks do not prove the whole cloud run succeeded, but they help catch formatting and code issues early.

Architecture placeholder:

![Architecture Placeholder](docs/images/architecture-overview.png)

## Naming Conventions

### Tables

- `raw_`: untouched data from source
- `stg_`: cleaned and casted staging data
- `fct_`: final analysis tables

### Terraform

Resource names use underscores, for example `google_storage_bucket.data_lake`.

### Bruin

Tasks are named by action, for example `ingest_kaggle` and `transform_genre_by_year`.

## Structure

```text
amazon-bestsellers-analytics-pipeline
├── .github/workflows/
├── infrastructure/
│   ├── gcp/
│   └── local/
├── pipeline/
│   ├── assets/
│   ├── ingestion/
│   └── transformations/
├── dashboard/
├── Makefile
├── README.md
└── ARCHITECTURE.md
```

## Project Theme

The current analytical focus is on four questions supported by the dataset:

- which authors appear most often in the bestseller dataset
- what nationality dominates in the dataset
- which genres dominate the dataset overall
- which genres dominate the dataset per year

The pipeline supports loading raw source data, standardizing it into staging models, and producing analytical fact tables for downstream reporting and dashboarding.

## Cloud Components

The cloud deployment now includes real IaC under [`infrastructure/gcp/`](/home/admin/data-engineering/amz-bestsellers-la/infrastructure/gcp):

- GCS raw data lake bucket
- BigQuery `raw` dataset
- BigQuery `analytics` dataset
- service account and IAM bindings for the pipeline

## Dataset Enrichment

The dataset is enriched with an author dimension workflow:

- `dim_authors` extracts the unique set of authors from `stg_bestsellers`
- `raw_author_nationality` stores a curated lookup of author to nationality
- `dim_author_nationality` joins the author list with the nationality lookup

Current seed status:

- `248` distinct author values extracted from `bestsellers_with_categories.csv`
- `248` author rows present in the nationality seed
- `7` entries currently marked as `Unknown` because they are organizations, pen names, or low-confidence matches

Starter files:

- [`dim_authors.sql`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/transformations/dim_authors.sql)
- [`dim_author_nationality.sql`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/transformations/dim_author_nationality.sql)
- [`author_nationality_seed.csv`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/assets/author_nationality_seed.csv)

## Analytical Models

The core SQL models for the supported dashboard questions are:

- [`stg_bestsellers.sql`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/transformations/stg_bestsellers.sql)
- [`fct_author_appearances.sql`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/transformations/fct_author_appearances.sql)
- [`fct_nationality_distribution.sql`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/transformations/fct_nationality_distribution.sql)
- [`fct_genre_overall.sql`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/transformations/fct_genre_overall.sql)
- [`fct_genre_by_year.sql`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/transformations/fct_genre_by_year.sql)

## Batch Orchestration

The Bruin pipeline definition lives at [`pipeline.yml`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/pipeline.yml) and the runnable assets live under [`pipeline/assets/`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/assets).

The end-to-end batch flow includes multiple steps:

1. seed `raw_bestsellers`
2. seed `raw_author_nationality`
3. run `ingest_raw_files` as the raw ingestion step
4. build `stg_bestsellers`
5. build dimensions and fact tables

This satisfies the multiple-step DAG requirement and includes a raw data lake upload step through [`upload_to_gcs.py`](/home/admin/data-engineering/amz-bestsellers-la/pipeline/ingestion/upload_to_gcs.py).

## Partitioning And Clustering

The warehouse strategy is designed around the dashboard queries:

- `stg_bestsellers` is partitioned by `year` and clustered by `genre, author`
- `fct_genre_by_year` is partitioned by `year` and clustered by `genre`
- `fct_author_appearances` is clustered by `author`
- `fct_nationality_distribution` is clustered by `nationality`

This makes sense because the main queries group by year, genre, author, and nationality.

## Dashboard

The Streamlit app at [`app.py`](/home/admin/data-engineering/amz-bestsellers-la/dashboard/app.py) visualizes the same four questions directly from the local asset files and includes more than two tiles.

Recommended screenshots to place in `docs/images/`:

- `step-01-infrastructure-setup.png`
- `step-02-pipeline-run.png`
- `step-03-dashboard.png`
- `architecture-overview.png`
- `dashboard-authors-tile.png`
- `dashboard-genres-tile.png`

Additional dashboard placeholders:

![Authors Tile Placeholder](docs/images/dashboard-authors-tile.png)

![Genres Tile Placeholder](docs/images/dashboard-genres-tile.png)

## Reproducibility

To reproduce the project:

1. install dependencies from [`requirements.txt`](/home/admin/data-engineering/amz-bestsellers-la/requirements.txt)
2. enable the required GCP APIs
3. authenticate with `service-account.json`
4. provision GCP resources with Terraform
5. configure Bruin using [`.bruin.yml.example`](/home/admin/data-engineering/amz-bestsellers-la/.bruin.yml.example)
6. upload the raw files from `pipeline/assets/` to GCS
7. run the Bruin pipeline
8. validate the infrastructure and data with the smoke tests above
9. launch the Streamlit dashboard

## CI/CD

The project includes [`.github/workflows/main.yml`](/home/admin/data-engineering/amz-bestsellers-la/.github/workflows/main.yml) to:

- run `bruin format --check`
- run `bruin validate`
- execute `bruin dry-run`
- check Terraform formatting with `terraform fmt -check -recursive`
- compile the Python application and ingestion files

### GitHub Actions With GCP Workload Identity Federation

For CI, the repository is configured to authenticate to Google Cloud using Workload Identity Federation instead of storing a long-lived service account key in GitHub.

Create these GitHub repository values:

Secrets:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`

Variables:

- `GCP_PROJECT_ID`
- `GCP_REGION`

Recommended default:

- `GCP_REGION=us-central1`

Important note:

- `project_id` is not a secret
- `GCP_PROJECT_ID` should be stored as a GitHub Actions repository variable, not a secret
- the Workload Identity Provider resource name is generally treated as configuration, but storing it as a secret is acceptable if you prefer to keep your CI settings centralized
- the sensitive part is the credential itself, which WIF avoids storing in GitHub
