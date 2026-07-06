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
from unittest.mock import patch
from wsgi import app
from service.models import Wishlist, Item, DataValidationError, db
from tests.factories import WishlistFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#        W I S H L I S T   M O D E L   T E S T   C A S E S
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
        """It should Create a wishlist and assert that it exists"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        wishlist = WishlistFactory()
        wishlist.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)

        found = Wishlist.all()
        self.assertEqual(len(found), 1)

        data = Wishlist.find(wishlist.id)
        self.assertEqual(data.name, wishlist.name)
        self.assertEqual(data.customer_id, wishlist.customer_id)
        self.assertEqual(data.description, wishlist.description)

    @patch("service.models.db.session.commit")
    def test_create_wishlist_failed(self, exception_mock):
        """It should not create a Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.create)

    def test_read_a_wishlist(self):
        """It should Read a wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Read it back
        found = Wishlist.find(wishlist.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, wishlist.id)
        self.assertEqual(found.name, wishlist.name)
        self.assertEqual(found.customer_id, wishlist.customer_id)
        self.assertEqual(found.description, wishlist.description)

    def test_update_a_wishlist(self):
        """It should Update a wishlist"""
        wishlist = WishlistFactory(name="Default")
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        wishlist = Wishlist.find(wishlist.id)
        self.assertIsNotNone(wishlist.id)
        self.assertEqual(wishlist.name, "Default")

        # Update the name
        wishlist.name = "Updated"
        wishlist.update()
        # Fetch it back
        wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(wishlist.name, "Updated")

    @patch("service.models.db.session.commit")
    def test_update_wishlist_failed(self, exception_mock):
        """It should not update a Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.update)

    def test_delete_a_wishlist(self):
        """It should Delete a wishlist from the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        wishlist = wishlists[0]
        wishlist.delete()
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 0)

    @patch("service.models.db.session.commit")
    def test_delete_wishlist_failed(self, exception_mock):
        """It should not delete a Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.delete)

    def test_list_all_wishlists(self):
        """It should List all wishlists"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        wishlists = WishlistFactory.create_batch(5)
        for wishlist in wishlists:
            wishlist.create()

        # Assert that there are 5 accounts in the database
        found = Wishlist.all()
        self.assertEqual(len(found), 5)

    def test_find_by_name(self):
        """It should Find a Wishlist by name"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Fetch it back by name
        same_wishlist = Wishlist.find_by_name(wishlist.name)[0]
        self.assertEqual(same_wishlist.id, wishlist.id)
        self.assertEqual(same_wishlist.name, wishlist.name)



    def test_find_by_customer_id(self):
        """It should Find Wishlists by customer_id"""
        customer_id = 123

        wishlist1 = WishlistFactory(customer_id=customer_id)
        wishlist1.create()
        wishlist2 = WishlistFactory(customer_id=customer_id)
        wishlist2.create()
        wishlist3 = WishlistFactory(customer_id=456)
        wishlist3.create()
        wishlists = Wishlist.find_by_customer_id(customer_id)

        self.assertEqual(wishlists.count(), 2)

        for wishlist in wishlists:
            self.assertEqual(wishlist.customer_id, customer_id)




    def test_serialize_a_wishlist(self):
        """It should Serialize a wishlist"""
        wishlist = WishlistFactory()
        item = ItemFactory()
        wishlist.items.append(item)

        serial_wishlist = wishlist.serialize()
        self.assertEqual(serial_wishlist["id"], wishlist.id)
        self.assertEqual(serial_wishlist["name"], wishlist.name)
        self.assertEqual(serial_wishlist["customer_id"], wishlist.customer_id)
        self.assertEqual(serial_wishlist["description"], wishlist.description)
        self.assertEqual(len(serial_wishlist["items"]), 1)

        items = serial_wishlist["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["wishlist_id"], item.wishlist_id)
        self.assertEqual(items[0]["name"], item.name)
        self.assertEqual(items[0]["quantity"], item.quantity)

    def test_deserialize_a_wishlist(self):
        """It should Deserialize a wishlist"""
        wishlist = WishlistFactory()
        wishlist.items.append(ItemFactory())
        serial_wishlist = wishlist.serialize()
        new_wishlist = Wishlist()
        new_wishlist.deserialize(serial_wishlist)

        self.assertEqual(wishlist.name, new_wishlist.name)
        self.assertEqual(wishlist.customer_id, new_wishlist.customer_id)
        self.assertEqual(wishlist.description, new_wishlist.description)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize a wishlist with a KeyError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize a wishlist with a TypeError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, [])

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an item with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an item with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])
