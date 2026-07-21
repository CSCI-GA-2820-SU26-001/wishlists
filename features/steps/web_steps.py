"""
Step definitions for Wishlist BDD tests
"""

import requests
from behave import given, when, then


@given("the Wishlist BDD test environment is configured")
def step_impl(context):
    """Verify that the BDD test environment is configured"""
    assert context.base_url is not None


@given("the wishlist service is running")
def step_impl(context):
    """Verify that the wishlist service is running"""
    response = requests.get(f"{context.base_url}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"

@given("a wishlist exists")
def step_impl(context):
    """Create a wishlist for update testing"""
    payload = {
        "customer_id": 1001,
        "name": "Original Wishlist",
        "description": "Original description",
        "items": [],
    }

    response = requests.post(
        f"{context.base_url}/wishlists",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 201

    context.wishlist = response.json()
    context.wishlist_id = context.wishlist["id"]

@when(
    'I create a wishlist with customer id "{customer_id}", '
    'name "{name}", and description "{description}"'
)
def step_impl(context, customer_id, name, description):
    """Create a wishlist through the REST API"""
    payload = {
        "customer_id": int(customer_id),
        "name": name,
        "description": description,
        "items": [],
    }

    context.response = requests.post(
        f"{context.base_url}/wishlists",
        json=payload,
        timeout=5,
    )

@when(
    'I update the wishlist with customer id "{customer_id}", '
    'name "{name}", and description "{description}"'
)
def step_impl(context, customer_id, name, description):
    """Update an existing wishlist"""
    payload = {
        "customer_id": int(customer_id),
        "name": name,
        "description": description,
        "items": [],
    }

    context.response = requests.put(
        f"{context.base_url}/wishlists/{context.wishlist_id}",
        json=payload,
        timeout=5,
    )

@then("the response status code should be {status_code:d}")
def step_impl(context, status_code):
    """Check the response status code"""
    assert context.response.status_code == status_code


@then('the response should contain customer id "{customer_id}"')
def step_impl(context, customer_id):
    """Check the customer id in the response"""
    data = context.response.json()
    assert data["customer_id"] == int(customer_id)


@then('the response should contain name "{name}"')
def step_impl(context, name):
    """Check the wishlist name in the response"""
    data = context.response.json()
    assert data["name"] == name


@then('the response should contain description "{description}"')
def step_impl(context, description):
    """Check the wishlist description in the response"""
    data = context.response.json()
    assert data["description"] == description

@given(
    'a wishlist exists with customer id "{customer_id}", '
    'name "{name}", and description "{description}"'
)
def step_impl(context, customer_id, name, description):
    """Create a wishlist fixture for delete tests"""
    payload = {
        "customer_id": int(customer_id),
        "name": name,
        "description": description,
        "items": [],
    }

    response = requests.post(
        f"{context.base_url}/wishlists",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 201, (
        f"Expected 201 when creating test wishlist, "
        f"got {response.status_code}: {response.text}"
    )

    data = response.json()
    context.wishlist_id = data["id"]
    context.response = response


@when("I delete the wishlist")
def step_impl(context):
    """Delete the wishlist through the REST API"""
    context.response = requests.delete(
        f"{context.base_url}/wishlists/{context.wishlist_id}",
        timeout=5,
    )


@then("the wishlist should no longer be available")
def step_impl(context):
    """Verify that the deleted wishlist returns 404"""
    response = requests.get(
        f"{context.base_url}/wishlists/{context.wishlist_id}",
        timeout=5,
    )

    assert response.status_code == 404, (
        f"Expected deleted wishlist to return 404, "
        f"got {response.status_code}: {response.text}"
    )