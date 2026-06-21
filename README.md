# Wishlists Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

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

Future wishlist item support will include product items that belong to a wishlist.

## Current API

### Root Endpoint

```http
GET /
```

Returns basic information about the service.

Example response:

```json
{
  "name": "Wishlists Service",
  "version": "1.0.0",
  "list_url": "/wishlists"
}
```

## Planned API Endpoints

The following endpoints are planned for the Wishlists service:

```text
POST   /wishlists
GET    /wishlists
GET    /wishlists/{wishlist_id}
PUT    /wishlists/{wishlist_id}
DELETE /wishlists/{wishlist_id}
```

The following item endpoints are planned for wishlist items:

```text
POST   /wishlists/{wishlist_id}/items
GET    /wishlists/{wishlist_id}/items
GET    /wishlists/{wishlist_id}/items/{item_id}
PUT    /wishlists/{wishlist_id}/items/{item_id}
DELETE /wishlists/{wishlist_id}/items/{item_id}
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

## License

Copyright (c) 2016, 2025 John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE).

This repository is part of the New York University CSCI-GA.2820-001 DevOps and Agile Methodologies course.
