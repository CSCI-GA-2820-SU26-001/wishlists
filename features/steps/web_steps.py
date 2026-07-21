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