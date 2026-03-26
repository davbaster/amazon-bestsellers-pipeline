provider "docker" {}

resource "docker_image" "postgres" {
  name         = "postgres:16"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name  = "amz-bestsellers-postgres"
  image = docker_image.postgres.image_id

  env = [
    "POSTGRES_DB=amz_bestsellers",
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=postgres",
  ]

  ports {
    internal = 5432
    external = 5432
  }
}
