######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0
######################################################################

"""
Test cases for Wishlist Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Wishlist, DataValidationError, db
from .factories import WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  W I S H L I S T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlistModel(TestCase):
    """Test Cases for Wishlist Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_wishlist(self):
        """It should Create a wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        self.assertIsNotNone(wishlist.id)

        found = Wishlist.all()
        self.assertEqual(len(found), 1)

        data = Wishlist.find(wishlist.id)
        self.assertEqual(data.name, wishlist.name)
        self.assertEqual(data.customer_id, wishlist.customer_id)

    def test_read_a_wishlist(self):
        """It should Read a wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        found = Wishlist.find(wishlist.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, wishlist.id)
        self.assertEqual(found.name, wishlist.name)
        self.assertEqual(found.customer_id, wishlist.customer_id)

    def test_update_a_wishlist(self):
        """It should Update a wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        self.assertIsNotNone(wishlist.id)

        wishlist.name = "Updated Wishlist"
        wishlist.update()

        found = Wishlist.find(wishlist.id)
        self.assertEqual(found.name, "Updated Wishlist")

    def test_delete_a_wishlist(self):
        """It should Delete a wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        self.assertEqual(len(Wishlist.all()), 1)

        wishlist.delete()

        self.assertEqual(len(Wishlist.all()), 0)

    def test_list_all_wishlists(self):
        """It should List all wishlists"""
        wishlists = WishlistFactory.create_batch(5)

        for wishlist in wishlists:
            wishlist.create()

        found = Wishlist.all()
        self.assertEqual(len(found), 5)

    def test_serialize_a_wishlist(self):
        """It should Serialize a wishlist"""
        wishlist = WishlistFactory()
        data = wishlist.serialize()

        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("customer_id", data)
        self.assertEqual(data["name"], wishlist.name)
        self.assertEqual(data["customer_id"], wishlist.customer_id)

    def test_deserialize_a_wishlist(self):
        """It should Deserialize a wishlist"""
        data = {
            "name": "Birthday Wishlist",
            "customer_id": 1001,
        }

        wishlist = Wishlist()
        wishlist.deserialize(data)

        self.assertEqual(wishlist.name, "Birthday Wishlist")
        self.assertEqual(wishlist.customer_id, 1001)

    def test_deserialize_with_missing_name(self):
        """It should not Deserialize a wishlist without a name"""
        data = {
            "customer_id": 1001,
        }

        wishlist = Wishlist()

        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_deserialize_with_missing_customer_id(self):
        """It should not Deserialize a wishlist without a customer_id"""
        data = {
            "name": "Birthday Wishlist",
        }

        wishlist = Wishlist()

        self.assertRaises(DataValidationError, wishlist.deserialize, data)