"""
Step definitions for Wishlist BDD tests
"""

from shutil import which

import requests
from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "/api/wishlists"


def get_driver(context):
    """Create a Selenium WebDriver if one does not already exist."""
    if context.driver is None:
        options = Options()
        chromium = which("chromium")
        if chromium:
            options.binary_location = chromium
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        chromedriver = which("chromedriver")
        if chromedriver:
            service = Service(chromedriver)
            context.driver = webdriver.Chrome(service=service, options=options)
        else:
            context.driver = webdriver.Chrome(options=options)
    return context.driver


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
        f"{context.base_url}{BASE_URL}",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 201

    context.wishlist = response.json()
    context.wishlist_id = context.wishlist["id"]


@given("multiple wishlists exist")
def step_impl(context):
    wishlists = [
        {
            "customer_id": 1001,
            "name": "Wishlist One",
            "description": "First wishlist",
            "items": [],
        },
        {
            "customer_id": 1001,
            "name": "Wishlist Two",
            "description": "Second wishlist",
            "items": [],
        },
        {
            "customer_id": 2001,
            "name": "Wishlist Three",
            "description": "Third wishlist",
            "items": [],
        },
    ]

    for wishlist in wishlists:
        response = requests.post(
            f"{context.base_url}{BASE_URL}",
            json=wishlist,
            timeout=5,
        )
        assert response.status_code == 201


@given("an item exists in the wishlist")
def step_impl(context):
    """Create an item for delete testing"""
    payload = {
        "wishlist_id": context.wishlist_id,
        "name": "MacBook",
        "quantity": 1,
    }

    response = requests.post(
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}/items",
        json=payload,
        timeout=5,
    )

    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}: {response.text}"

    context.item = response.json()
    context.item_id = context.item["id"]


@given("multiple items exist in the wishlist")
def step_impl(context):
    """Create multiple items in the wishlist"""
    items = [
        {"wishlist_id": context.wishlist_id, "name": "MacBook", "quantity": 1},
        {"wishlist_id": context.wishlist_id, "name": "iPhone", "quantity": 2},
        {"wishlist_id": context.wishlist_id, "name": "iPad", "quantity": 3},
    ]

    context.items = []

    for item in items:
        response = requests.post(
            f"{context.base_url}{BASE_URL}/{context.wishlist_id}/items",
            json=item,
            timeout=5,
        )

        assert response.status_code == 201

        context.items.append(response.json())


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
        f"{context.base_url}{BASE_URL}",
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
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}",
        json=payload,
        timeout=5,
    )


@when('I query wishlists with customer id "{customer_id}"')
def step_impl(context, customer_id):
    context.response = requests.get(
        f"{context.base_url}{BASE_URL}",
        params={"customer_id": customer_id},
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


@then('only wishlists for customer id "{customer_id}" are returned')
def step_impl(context, customer_id):
    wishlists = context.response.json()

    assert len(wishlists) > 0

    for wishlist in wishlists:
        assert str(wishlist["customer_id"]) == customer_id


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
        f"{context.base_url}{BASE_URL}",
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
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}",
        timeout=5,
    )


@when("I delete the item")
def step_impl(context):
    """Delete the item through the REST API"""
    context.response = requests.delete(
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}/items/{context.item_id}",
        timeout=5,
    )


@then("the wishlist should no longer be available")
def step_impl(context):
    """Verify that the deleted wishlist returns 404"""
    response = requests.get(
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}",
        timeout=5,
    )

    assert response.status_code == 404, (
        f"Expected deleted wishlist to return 404, "
        f"got {response.status_code}: {response.text}"
    )


@then("the item should no longer be available")
def step_impl(context):
    """Verify that the deleted item returns 404"""
    response = requests.get(
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}/items/{context.item_id}",
        timeout=5,
    )

    assert response.status_code == 404, (
        f"Expected deleted item to return 404, "
        f"got {response.status_code}: {response.text}"
    )


@when("I request the wishlist")
def step_impl(context):
    """Read the wishlist through the REST API"""
    context.response = requests.get(
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}",
        timeout=5,
    )


@when("I request the item")
def step_impl(context):
    """Read an item through the REST API"""
    context.response = requests.get(
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}/items/{context.item_id}",
        timeout=5,
    )


@when("I request all items")
def step_impl(context):
    """List all items in the wishlist"""
    context.response = requests.get(
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}/items",
        timeout=5,
    )


@when('I update the item with name "{name}" and quantity "{quantity}"')
def step_impl(context, name, quantity):
    """Update an existing item"""
    payload = {
        "wishlist_id": context.wishlist_id,
        "name": name,
        "quantity": int(quantity),
    }

    context.response = requests.put(
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}/items/{context.item_id}",
        json=payload,
        timeout=5,
    )


@when("I request all wishlists")
def step_impl(context):
    """List all wishlists through the REST API"""
    context.response = requests.get(
        f"{context.base_url}{BASE_URL}",
        timeout=5,
    )


@then('the response list should contain wishlist named "{name}"')
def step_impl(context, name):
    """Check that the wishlist list contains a wishlist by name"""
    data = context.response.json()
    names = [wishlist["name"] for wishlist in data]

    assert (
        name in names
    ), f"Expected wishlist named '{name}' in response list, got {data}"


@then("the response should contain the item information")
def step_impl(context):
    """Verify the returned item information"""
    data = context.response.json()

    assert data["id"] == context.item_id
    assert data["wishlist_id"] == context.wishlist_id
    assert data["name"] == context.item["name"]
    assert data["quantity"] == context.item["quantity"]


@then('the response should contain item name "{name}"')
def step_impl(context, name):
    """Verify updated item name"""
    data = context.response.json()
    assert data["name"] == name


@then("the response should contain all existing items")
def step_impl(context):
    """Verify all existing items are returned"""
    data = context.response.json()

    assert len(data) == len(context.items)

    returned_names = [item["name"] for item in data]
    expected_names = [item["name"] for item in context.items]

    for name in expected_names:
        assert name in returned_names


@when("I clear all items from the wishlist through the web UI")
def step_impl(context):
    """Clear all items from the active wishlist through the browser UI."""
    base_url = context.base_url.rstrip("/") + "/"

    driver = get_driver(context)
    driver.get(base_url)

    wishlist_id_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "wishlist_id"))
    )
    wishlist_id_input.clear()
    wishlist_id_input.send_keys(str(context.wishlist_id))

    driver.find_element(By.ID, "retrieve-btn").click()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.ID, "active_wishlist_id"),
            str(context.wishlist_id),
        )
    )

    driver.find_element(By.ID, "item-search-btn").click()
    driver.find_element(By.ID, "item-clear-btn").click()

    WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element(By.ID, "flash_message").text
        in ("Items cleared", "Success")
    )


@when("I search for items in the wishlist through the web UI")
def step_impl(context):
    """Refresh item search results through the browser UI."""
    driver = get_driver(context)
    driver.find_element(By.ID, "item-search-btn").click()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.ID, "flash_message"),
            "Success",
        )
    )


@then("the wishlist should still exist")
def step_impl(context):
    """Verify the wishlist still exists after clearing its items."""
    base_url = context.base_url.rstrip("/")
    response = requests.get(
        f"{base_url}/api/wishlists/{context.wishlist_id}",
        timeout=5,
    )
    assert response.status_code == 200


@then("the wishlist should contain no items")
def step_impl(context):
    """Verify the item search results are empty."""
    driver = get_driver(context)
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "#item_search_results table tbody tr",
    )
    assert len(rows) == 0, f"Expected no items, but found {len(rows)}"


@then('the response should contain quantity "{quantity}"')
def step_impl(context, quantity):
    """Verify updated item quantity"""
    data = context.response.json()
    assert data["quantity"] == int(quantity)


@when('I create an item with name "{name}" and quantity "{quantity}"')
def step_impl(context, name, quantity):
    """Create an item through the REST API"""
    payload = {
        "wishlist_id": int(context.wishlist_id),
        "name": name,
        "quantity": int(quantity),
    }

    context.response = requests.post(
        f"{context.base_url}{BASE_URL}/{context.wishlist_id}/items",
        json=payload,
        timeout=5,
    )


@then("the response should contain the correct wishlist id")
def step_impl(context):
    """Verify the created item has the right wishlist_id"""
    data = context.response.json()
    assert data["wishlist_id"] == int(context.wishlist_id)
