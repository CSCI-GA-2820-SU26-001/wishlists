"""
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .item import Item

logger = logging.getLogger("flask.app")


######################################################################
#  W I S H L I S T   M O D E L
######################################################################
class Wishlist(db.Model, PersistentBase):
    """
    Class that represents an Wishlist
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(256), nullable=True)
    items = db.relationship("Item", backref="wishlist", passive_deletes=True)

    def __repr__(self):
        return f"<Wishlist {self.name} id=[{self.id}]>"

    def serialize(self) -> dict:
        """Converts a Wishlist into a dictionary"""
        wishlist = {
            "id": self.id,
            "name": self.name,
            "customer_id": self.customer_id,
            "description": self.description,
            "items": [],
        }
        for item in self.items:
            wishlist["items"].append(item.serialize())
        return wishlist

    def deserialize(self, data: dict) -> None:
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the wishlist data
        """
        try:
            # id is  excluded from deserialization
            # since clients shouldn't set their own ID
            self.name = data["name"]
            self.customer_id = data["customer_id"]
            self.description = data.get("description")  # nullable
            # handle inner list of addresses
            item_list = data.get("items", [])  # can be empty
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained bad or no data "
                + str(error)
            ) from error

    @classmethod
    def find_by_name(cls, name):
        """
        Returns all Wishlists with the given name

        Args:
            name (string): the name of the Accounts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
