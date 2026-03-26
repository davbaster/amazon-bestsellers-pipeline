output "data_lake_bucket_name" {
  value       = google_storage_bucket.data_lake.name
  description = "Name of the raw data lake bucket."
}

output "raw_dataset_id" {
  value       = google_bigquery_dataset.raw.dataset_id
  description = "Raw dataset id."
}

output "analytics_dataset_id" {
  value       = google_bigquery_dataset.analytics.dataset_id
  description = "Analytics dataset id."
}

output "pipeline_service_account_email" {
  value       = google_service_account.pipeline.email
  description = "Service account used by the cloud batch pipeline."
}
