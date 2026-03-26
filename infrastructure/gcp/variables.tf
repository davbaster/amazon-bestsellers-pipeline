variable "project_id" {
  description = "GCP project id used for all resources."
  type        = string
}

variable "region" {
  description = "Primary GCP region."
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "Optional override for the raw data lake bucket."
  type        = string
  default     = null
}

variable "service_account_id" {
  description = "Service account id for the batch pipeline."
  type        = string
  default     = "amz-bestsellers-pipeline"
}
