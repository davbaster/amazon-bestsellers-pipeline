.PHONY: infra-gcp infra-local pipeline pipeline-cloud upload-raw dashboard test

infra-gcp:
	cd infrastructure/gcp && terraform apply

infra-local:
	cd infrastructure/local && terraform apply

pipeline:
	bruin run

pipeline-cloud:
	bruin run pipeline/pipeline.yml

upload-raw:
	python3 pipeline/ingestion/upload_to_gcs.py

dashboard:
	streamlit run dashboard/app.py

test:
	bruin validate
	terraform fmt -check
