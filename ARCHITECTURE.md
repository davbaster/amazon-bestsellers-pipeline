# Architecture

## Data Engineering Architecture: Bestseller Analytics

This project analyzes Amazon bestseller behavior through a focused DataOps workflow built on Bruin, Terraform, and GCP.

## Overview

The platform is designed to answer a small set of dataset-supported analytical questions around author frequency, nationality coverage, and genre dominance.

At a high level, the system will:

1. upload batch files into a cloud raw data lake
2. standardize and clean records in staging models
3. create analytical fact tables for author and genre analysis
4. serve results to a Streamlit dashboard

## Technical Stack

- Orchestration: Bruin, a lightweight SQL-first orchestrator
- Infrastructure: Terraform with a dual-provider approach for GCP and Docker
- Storage: BigQuery for cloud execution and PostgreSQL for local execution
- CI/CD: GitHub Actions for automated testing and pipeline validation

## CI/CD Workflow

The repository uses two GitHub Actions workflows:

- [`.github/workflows/ci.yml`](/home/admin/data-engineering/amz-bestsellers-la/.github/workflows/ci.yml) for lightweight pull request and push checks
- [`.github/workflows/integration-cloud.yml`](/home/admin/data-engineering/amz-bestsellers-la/.github/workflows/integration-cloud.yml) for manual cloud integration validation

The split is intentional:

- `ci.yml` performs fast static checks that do not require cloud infrastructure to exist
- `integration-cloud.yml` provisions infrastructure, uploads raw data, runs the Bruin pipeline, and executes smoke tests against BigQuery

## Deployment Model

### Cloud

- Terraform provisions GCP resources such as GCS, BigQuery datasets, and IAM bindings
- a Python batch ingestion step uploads raw files into GCS
- Bruin orchestrates the seed, ingestion, staging, dimension, and fact tasks
- BigQuery stores analytical models used by the dashboard

### Local

- local assets can be stored under `pipeline/assets/`
- local infrastructure can use Docker-backed services under `infrastructure/local/`

## Naming Conventions

### Data Modeling

- `raw_` for source-aligned tables with no business transformations
- `stg_` for cleaned, typed, and standardized staging tables
- `fct_` for final analytical fact tables

### Infrastructure as Code

Terraform resource identifiers should use underscores.

Example:

```hcl
resource "google_storage_bucket" "data_lake" {
  name = "amazon-bestsellers-analytics-data-lake"
}
```

### Orchestration

Bruin task names should describe the action they perform.

Examples:

- `ingest_kaggle`
- `transform_genre_by_year`

## Data Layers

- `raw_` tables preserve source fidelity for reproducibility
- `stg_` tables normalize schemas, data types, and business logic inputs
- `fct_` tables support final analytical outputs and dashboard-ready summaries

## Author Enrichment Design

To support author nationality analysis, the project adds a lightweight dimension flow:

1. `dim_authors` extracts the distinct authors from `stg_bestsellers`
2. `raw_author_nationality` stores the author-to-nationality lookup
3. `dim_author_nationality` exposes the joined author dimension for downstream analysis

This keeps source book records separate from slowly changing author metadata and makes it easier to improve enrichment quality over time.

Current enrichment coverage:

- `248` distinct author values identified in the source dataset
- `248` rows curated in the nationality lookup seed
- `7` rows still marked as `Unknown` for unresolved or non-person entities

## Data Modeling Logic

The transformation layer is organized around the supported business questions.

### Supported Outputs

- `fct_author_appearances` counts how often each author appears in the dataset
- `fct_nationality_distribution` summarizes author nationality coverage and bestseller-row dominance
- `fct_genre_overall` measures the overall fiction versus non-fiction split
- `fct_genre_by_year` tracks genre counts and rankings for each year

## Batch DAG

The batch pipeline is intentionally multi-step so the orchestration layer is visible in the project:

1. `raw_bestsellers` loads the source CSV into BigQuery
2. `raw_author_nationality` loads the nationality lookup seed
3. `ingest_raw_files` uploads source files to GCS as the raw data lake step
4. `stg_bestsellers` standardizes the source schema
5. `dim_authors` and `dim_author_nationality` build reusable dimensions
6. `fct_author_appearances`, `fct_nationality_distribution`, `fct_genre_overall`, and `fct_genre_by_year` build dashboard-facing tables

## Partitioning And Clustering Strategy

The upstream query patterns are dominated by filters and aggregations on `year`, `genre`, `author`, and `nationality`.

Chosen strategy:

- `stg_bestsellers`: partition by `year_partition_date`, cluster by `genre` and `author`
- `fct_genre_by_year`: partition by `year_partition_date`, cluster by `genre`
- `fct_author_appearances`: cluster by `author`
- `fct_nationality_distribution`: cluster by `nationality`

This reduces scan costs for the dashboard and keeps the largest analytical tables aligned with the grouping dimensions used most often.

### Transformation Snippet (Bruin SQL)

```sql
-- transformations/fct_genre_by_year.sql
WITH genre_counts AS (
    SELECT
        year,
        genre,
        COUNT(*) AS bestseller_rows
    FROM {{ ref('stg_bestsellers') }}
    GROUP BY year, genre
)

SELECT
    year,
    genre,
    bestseller_rows
FROM genre_counts
```

## Suggested Analytical Focus

- author concentration and repeat bestseller presence
- nationality dominance in the dataset
- overall genre balance
- yearly genre shifts and turning points
