provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  data_lake_bucket = coalesce(var.bucket_name, "${var.project_id}-amz-bestsellers-raw")
  labels = {
    project = "amazon-bestsellers"
    managed = "terraform"
  }
}

resource "google_storage_bucket" "data_lake" {
  name                        = local.data_lake_bucket
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true
  storage_class               = "STANDARD"

  versioning {
    enabled = true
  }

  labels = local.labels
}

resource "google_bigquery_dataset" "raw" {
  dataset_id = "raw"
  location   = var.region
  labels     = local.labels
}

resource "google_bigquery_dataset" "analytics" {
  dataset_id = "analytics"
  location   = var.region
  labels     = local.labels
}

resource "google_service_account" "pipeline" {
  account_id   = var.service_account_id
  display_name = "Amazon Bestsellers Pipeline"
}

resource "google_project_iam_member" "pipeline_bigquery_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_project_iam_member" "pipeline_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_storage_bucket_iam_member" "pipeline_storage_admin" {
  bucket = google_storage_bucket.data_lake.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline.email}"
}
