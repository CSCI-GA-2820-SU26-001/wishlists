######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
TestWishlist API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from tests.factories import WishlistFactory, ItemFactory
from service.common import status
from service.models import db, Wishlist

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "api/wishlists"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class BaseTestCase(TestCase):
    """Base Test Case Setup"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Wishlists Demo REST API Service", resp.data)

    def test_create_wishlist(self):
        """It should Create a new Wishlist"""
        wishlist = WishlistFactory()
        resp = self.client.post(BASE_URL, json=wishlist.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        # location = resp.headers.get("Location", None)
        # self.assertIsNotNone(location)

        # Check the data is correct
        new_wishlist = resp.get_json()
        self.assertEqual(
            new_wishlist["name"], wishlist.name, "Wishlist name does not match"
        )
        self.assertEqual(
            new_wishlist["customer_id"],
            wishlist.customer_id,
            "Customer_id does not match",
        )
        self.assertEqual(
            new_wishlist["description"],
            wishlist.description,
            "Description does not match",
        )
        self.assertEqual(new_wishlist["items"], wishlist.items, "Items does not match")

    def test_list_wishlists_by_name(self):
        """It should List Wishlists by wishlist name"""
        name0 = "name 0"
        name1 = "name 1"

        wishlist1 = WishlistFactory(name=name0)
        wishlist1.create()

        wishlist2 = WishlistFactory(name=name0)
        wishlist2.create()

        wishlist3 = WishlistFactory(name=name1)
        wishlist3.create()

        resp = self.client.get(f"{BASE_URL}?name={name0}")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        self.assertEqual(len(data), 2)

        for wishlist in data:
            self.assertEqual(wishlist["name"], name0)

    def test_list_wishlists_by_customer_id(self):
        """It should List Wishlists by customer_id"""
        customer_id = 123

        wishlist1 = WishlistFactory(customer_id=customer_id)
        wishlist1.create()

        wishlist2 = WishlistFactory(customer_id=customer_id)
        wishlist2.create()

        wishlist3 = WishlistFactory(customer_id=456)
        wishlist3.create()

        resp = self.client.get(f"{BASE_URL}?customer_id={customer_id}")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        self.assertEqual(len(data), 2)

        for wishlist in data:
            self.assertEqual(wishlist["customer_id"], customer_id)

    def test_read_item(self):
        """It should read an Item"""

        # Create a wishlist directly

        wishlist = WishlistFactory()

        wishlist.create()

        # Create an item directly

        item = ItemFactory(wishlist=wishlist)

        item.create()

        # Read the item through API

        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items/{item.id}")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], item.id)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["quantity"], item.quantity)

    def test_list_items(self):
        """It should list all items in a wishlist"""

        wishlist = WishlistFactory()
        wishlist.create()

        item1 = ItemFactory(wishlist=wishlist)
        item1.create()

        item2 = ItemFactory(wishlist=wishlist)
        item2.create()

        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        self.assertEqual(len(data), 2)

    def test_get_wishlist(self):
        """It should Read a single Wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        resp = self.client.get(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], wishlist.id)
        self.assertEqual(data["name"], wishlist.name)
        self.assertEqual(data["customer_id"], wishlist.customer_id)

    def test_get_wishlist_not_found(self):
        """It should not Read a Wishlist that does not exist"""
        resp = self.client.get("{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # more cases will be added in the future

    def test_list_items_empty(self):
        """It should return an empty list"""

        wishlist = WishlistFactory()
        wishlist.create()

        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        self.assertEqual(data, [])

    def test_read_item_not_found(self):
        """It should return 404 for missing item"""

        wishlist = WishlistFactory()
        wishlist.create()

        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items/99999")

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_item(self):
        """It should add an Item to a Wishlist"""

        # Create a wishlist first
        wishlist = WishlistFactory()

        resp = self.client.post(BASE_URL, json=wishlist.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        created_wishlist = resp.get_json()

        # Create item data
        item = ItemFactory(wishlist_id=wishlist.id)

        # Add item to wishlist
        resp = self.client.post(
            f"{BASE_URL}/{created_wishlist['id']}/items",
            json=item.serialize(),
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()

        self.assertEqual(data["wishlist_id"], created_wishlist["id"])
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["quantity"], item.quantity)

    def test_update_item(self):
        """It should Update an Item"""
        wishlist = WishlistFactory()
        wishlist.create()

        item = ItemFactory(wishlist=wishlist)
        item.create()

        update_data = item.serialize()
        update_data["name"] = "Updated Item"
        update_data["quantity"] = 99

        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/items/{item.id}",
            json=update_data,
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        self.assertEqual(data["id"], item.id)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["name"], "Updated Item")
        self.assertEqual(data["quantity"], 99)

    def test_delete_item(self):
        """It should Delete an Item"""
        # create an item
        wishlist = self._create_wishlists(1)[0]
        item = ItemFactory()
        item.wishlist_id = wishlist.id
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items", json=item.serialize()
        )
        # make sure the item is created
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wishlist(self):
        """It should Delete a Wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        found = Wishlist.find(wishlist.id)
        self.assertIsNone(found)

    def test_delete_all_wishlists(self):
        """It should Delete all Wishlists"""
        # Create a few wishlists
        self._create_wishlists(3)

        # Confirm they exist
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

        # Delete all wishlists
        resp = self.client.delete(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

        # Confirm none remain
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_read_item_wishlist_not_found(self):
        """It should return 404 when reading an item from a missing wishlist"""
        resp = self.client.get(f"{BASE_URL}/0/items/1")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_item_wishlist_not_found(self):
        """It should return 404 when adding an item to a missing wishlist"""
        wishlist_id = 0
        item = ItemFactory()
        item.wishlist_id = wishlist_id
        resp = self.client.post(
            f"{BASE_URL}/{wishlist_id}/items", json=item.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_items_wishlist_not_found(self):
        """It should return 404 when listing items from a missing wishlist"""
        resp = self.client.get(f"{BASE_URL}/0/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_not_found(self):
        """It should return 404 when updating a missing item"""
        wishlist = WishlistFactory()
        wishlist.create()

        item = ItemFactory()
        data = item.serialize()

        resp = self.client.put(f"{BASE_URL}/{wishlist.id}/items/0", json=data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_wishlist_no_content_type(self):
        """It should return 415 when creating a wishlist without Content-Type"""
        resp = self.client.post(BASE_URL, data="{}")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_wishlist_wrong_content_type(self):
        """It should return 415 when creating a wishlist with wrong Content-Type"""
        resp = self.client.post(
            BASE_URL,
            data="{}",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_item_wishlist_not_found(self):
        """It should return 404 when updating an item in a missing wishlist"""
        item = ItemFactory()
        resp = self.client.put(f"{BASE_URL}/0/items/1", json=item.serialize())
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        """It should return 405 for unsupported method"""
        resp = self.client.put(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_wishlist(self):
        """It should Update a Wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        new_data = wishlist.serialize()
        new_data["name"] = "Updated Wishlist"
        new_data["description"] = "Updated description"

        resp = self.client.put(f"{BASE_URL}/{wishlist.id}", json=new_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], wishlist.id)
        self.assertEqual(data["name"], "Updated Wishlist")
        self.assertEqual(data["description"], "Updated description")

    def test_update_wishlist_not_found(self):
        """It should not Update a Wishlist that does not exist"""
        wishlist = WishlistFactory()
        data = wishlist.serialize()

        resp = self.client.put(f"{BASE_URL}/0", json=data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_wishlists(self):
        """It should List all Wishlists"""
        WishlistFactory().create()
        WishlistFactory().create()

        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_health(self):
        """It should return health status"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["status"], "OK")

    def test_clear_items(self):
        """It should clear all items from a wishlist"""

        # Create a wishlist
        wishlist = WishlistFactory()

        response = self.client.post(
            BASE_URL,
            json=wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_wishlist = response.get_json()

        # Add one item
        item = {
            "wishlist_id": wishlist.id,
            "name": "Coffee Maker",
            "quantity": 1,
        }

        response = self.client.post(
            f"{BASE_URL}/{new_wishlist['id']}/items",
            json=item,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Clear all items
        response = self.client.put(f"{BASE_URL}/{new_wishlist['id']}/items/clear")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify wishlist is empty
        response = self.client.get(f"{BASE_URL}/{new_wishlist['id']}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.get_json()), 0)

    def test_clear_items_not_found(self):
        """It should return 404 when clearing a missing wishlist"""

        response = self.client.post(f"{BASE_URL}/99999/clear")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_clear_empty_wishlist(self):
        """It should clear an empty wishlist"""

        wishlist = WishlistFactory()

        response = self.client.post(
            BASE_URL,
            json=wishlist.serialize(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_wishlist = response.get_json()

        response = self.client.put(f"{BASE_URL}/{new_wishlist['id']}/items/clear")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f"{BASE_URL}/{new_wishlist['id']}/items")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json(), [])

    def test_list_items_by_name(self):
        """It should List Items by item name"""
        name0 = "name 0"
        name1 = "name 1"
        wishlist = WishlistFactory()
        wishlist.create()
        item1 = ItemFactory(wishlist=wishlist, name=name0)
        item1.create()
        item2 = ItemFactory(wishlist=wishlist, name=name0)
        item2.create()
        item3 = ItemFactory(wishlist=wishlist, name=name1)
        item3.create()

        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items?name={name0}")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        self.assertEqual(len(data), 2)

        for item in data:
            self.assertEqual(item["name"], name0)

    # ---------------------------------------------------------------
    # helper function
    # ---------------------------------------------------------------
    def _create_wishlists(self, count):
        """Factory method to create wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.client.post(BASE_URL, json=wishlist.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Wishlist",
            )
            new_wishlist = resp.get_json()
            wishlist.id = new_wishlist["id"]
            wishlists.append(wishlist)
        return wishlists
