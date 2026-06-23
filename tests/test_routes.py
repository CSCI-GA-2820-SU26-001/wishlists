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

BASE_URL = "/wishlists"


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
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Wishlists Service")
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(data["list_url"], "/wishlists")

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


    def test_read_item(self):

        """It should read an Item"""

        # Create a wishlist directly

        wishlist = WishlistFactory()

        wishlist.create()

        # Create an item directly

        item = ItemFactory(wishlist=wishlist)

        item.create()

        # Read the item through API

        resp = self.client.get(

            f"/wishlists/{wishlist.id}/items/{item.id}"

        )

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

        resp = self.client.get(
            f"/wishlists/{wishlist.id}/items"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        self.assertEqual(len(data), 2)


    def test_list_items_empty(self):
        """It should return an empty list"""

        wishlist = WishlistFactory()
        wishlist.create()

        resp = self.client.get(
            f"/wishlists/{wishlist.id}/items"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()

        self.assertEqual(data, [])




    def test_read_item_not_found(self):
        """It should return 404 for missing item"""

        wishlist = WishlistFactory()
        wishlist.create()

        resp = self.client.get(
            f"/wishlists/{wishlist.id}/items/99999"
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_add_item(self):
        """It should add an Item to a Wishlist"""

        # Create a wishlist first
        wishlist = WishlistFactory()

        resp = self.client.post(BASE_URL, json=wishlist.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        created_wishlist = resp.get_json()

        # Create item data
        item = ItemFactory()
        item_data = item.serialize()
        item_data["wishlist_id"] = created_wishlist["id"]

        # Add item to wishlist
        resp = self.client.post(
            f"/wishlists/{created_wishlist['id']}/items",
            json=item_data,
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()

        self.assertEqual(data["wishlist_id"], created_wishlist["id"])
        self.assertEqual(data["name"], item_data["name"])
        self.assertEqual(data["quantity"], item_data["quantity"])



        # # Check that the location header was correct by getting it
        # resp = self.client.get(location)
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # new_wishlist = resp.get_json()
        # self.assertEqual(
        #     new_wishlist["name"], wishlist.name, "Wishlist name does not match"
        # )
        # self.assertEqual(
        #     new_wishlist["customer_id"],
        #     wishlist.customer_id,
        #     "Customer_id does not match",
        # )
        # self.assertEqual(
        #     new_wishlist["description"],
        #     wishlist.description,
        #     "Description does not match",
        # )
        # self.assertEqual(new_wishlist["items"], wishlist.items, "Items does not match")

    # more cases will be added in the future
