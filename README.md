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

## Quick Start

### Cloud Deployment

#### 1. Prerequisites

- Install Terraform
- Install Bruin CLI
- Install Python dependencies with `pip install -r requirements.txt`
- Create or use an existing GCP project
- Download a GCP service account JSON key and save it as `service-account.json`
- Copy `.bruin.yml.example` to `.bruin.yml` and fill in your GCP values

#### 2. Infrastructure Setup

```bash
cd infrastructure/gcp
terraform init
terraform apply -var="project_id=amz-bestsellers-analytics" -var="region=us-central1"
```

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

#### 4. Launch Dashboard

```bash
pip install streamlit
streamlit run dashboard/app.py
```

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

## Reproducibility

To reproduce the project:

1. install dependencies from [`requirements.txt`](/home/admin/data-engineering/amz-bestsellers-la/requirements.txt)
2. provision GCP resources with Terraform
3. configure Bruin using [`.bruin.yml.example`](/home/admin/data-engineering/amz-bestsellers-la/.bruin.yml.example)
4. upload the raw files to GCS
5. run the Bruin pipeline
6. launch the Streamlit dashboard

## CI/CD

The project includes [`.github/workflows/main.yml`](/home/admin/data-engineering/amz-bestsellers-la/.github/workflows/main.yml) to:

- run `bruin format --check`
- execute `bruin dry-run`
- check Terraform formatting with `terraform fmt -check -recursive`
