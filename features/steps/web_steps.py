"""
Step definitions for Wishlist BDD tests
"""

from behave import given
from selenium.webdriver.common.by import By


@given("the Wishlist BDD test environment is configured")
def step_impl(context):
    """Verify that the BDD test environment is configured"""
    assert context.base_url is not None
    assert By.ID == "id"
