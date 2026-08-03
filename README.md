# Wishlists Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-SU26-001/wishlists/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU26-001/wishlists/actions)
[![codecov](https://codecov.io/github/csci-ga-2820-su26-001/wishlists/graph/badge.svg?token=ZMKFYH04C7)](https://codecov.io/github/csci-ga-2820-su26-001/wishlists)

This repository contains the Wishlists microservice for the NYU DevOps and Agile Methodologies course project.

The Wishlists service allows customers to create and manage wishlists. A wishlist belongs to a customer and can contain multiple product items.

## Overview

The service is implemented with Python, Flask, SQLAlchemy, and PostgreSQL. It follows a RESTful API design and is developed using test-driven development.

Current core resource:

```text
Wishlist
```

A wishlist currently contains:

```text
id
name
customer_id
```

Wishlist item support is implemented. Each wishlist can contain multiple items.

## Current API

### Root Endpoint

```http
GET /
```

Returns the web UI for the Wishlists service.

### Health Endpoint

```http
GET /health
```

Returns the service health status.

### Swagger Documentation

```http
GET /apidocs
```

Opens the Swagger API documentation.

## API Endpoints

The following endpoints are supported by the Wishlists service:

```text
POST   /api/wishlists
GET    /api/wishlists
GET    /api/wishlists/{wishlist_id}
PUT    /api/wishlists/{wishlist_id}
DELETE /api/wishlists/{wishlist_id}
```

The following item endpoints are supported for wishlist items:

```text
POST   /api/wishlists/{wishlist_id}/items
GET    /api/wishlists/{wishlist_id}/items
GET    /api/wishlists/{wishlist_id}/items/{item_id}
PUT    /api/wishlists/{wishlist_id}/items/{item_id}
DELETE /api/wishlists/{wishlist_id}/items/{item_id}
```

## Project Structure

```text
service/
├── __init__.py
├── config.py
├── models.py
├── routes.py
└── common/
    ├── cli_commands.py
    ├── error_handlers.py
    ├── log_handlers.py
    └── status.py

tests/
├── __init__.py
├── factories.py
├── test_cli_commands.py
├── test_models.py
└── test_routes.py
```

## Running the Development Environment

Start the Docker development environment:

```bash
docker compose -f .devcontainer/docker-compose.yml up -d
```

Enter the application container:

```bash
docker exec -it nyu-project bash
```
The service will start using the configuration provided in the project environment files.
## Running Tests

Run all tests:

```bash
pytest
```

Run model and route tests without coverage:

```bash
pytest tests/test_models.py tests/test_routes.py --no-cov
```

## Running Lint

Run lint checks:

```bash
make lint
```

## Running the Service

Start the Flask service locally:

```bash
honcho start
```

The service will start using the configuration provided in the project environment files.

## Kubernetes Deployment

Kubernetes deployment manifests are located in the `k8s/` directory.

To deploy the application locally, run:

```bash
make cluster
make build
make push
make deploy
```

These commands create a local Kubernetes cluster, build the Docker image, push the image, and deploy the service.

## Continuous Integration

This project uses GitHub Actions for Continuous Integration.

Every push and pull request automatically runs:

- Unit tests
- Flake8 lint checks
- Pylint code quality checks
- Code coverage upload to Codecov.

## API Testing

The REST API can be tested using the REST Client extension in Visual Studio Code or any HTTP client such as curl or Postman.

## Final Project Notes

### Swagger API Documentation

Swagger API documentation is available at `/apidocs`.

When running locally, open:

```text
http://localhost:8080/apidocs
```

The root page also includes a link to the API documentation.

### API Prefix

The Flask-RESTX API uses the `/api` prefix.

Example endpoints:

```http
GET /api/wishlists
POST /api/wishlists
```

### BDD Tests

BDD tests are located in the `features/` directory and are written using Behave and Selenium.

Run BDD tests with:

```bash
pipenv run behave
```

To test against a deployed service, set `BASE_URL`:

```bash
BASE_URL=http://localhost:8080 pipenv run behave
```

### Tekton Pipeline

Tekton resources are located in the `tekton/` directory. The pipeline resources support tasks such as linting, testing, building the image, and deploying the service.

### OpenShift Deployment

The final OpenShift Route URL should be added after deployment:

```text
OpenShift Route URL: TBD after final deployment
```

After deployment, verify that:

```text
/health returns {"status": "OK"}
/apidocs opens successfully
BDD tests pass against the deployed route
```

## License

Copyright (c) 2016, 2025 John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE).

This repository is part of the New York University CSCI-GA.2820-001 DevOps and Agile Methodologies course.
