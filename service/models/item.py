"""
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, PersistentBase):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(
        db.Integer, db.ForeignKey("wishlist.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Item {self.name} id=[{self.id}] wishlist[{self.wishlist_id}]>"

    def __str__(self):
        return f"{self.name}: {self.quantity}"

    def serialize(self) -> dict:
        """Converts an Item into a dictionary"""
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "name": self.name,
            "quantity": self.quantity,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates an Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wishlist_id = data["wishlist_id"]
            self.name = data["name"]
            self.quantity = data["quantity"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data " + str(error)
            ) from error

    @classmethod
    def find_by_wishlist_and_name(cls, wishlist_id, name):
        """
        Returns all Items in a given Wishlist with the given name

        Args:
            wishlist_id (int): the wishlist to search within
            name (string): the name of the Item you want to match
        """
        logger.info("Processing name query for %s in wishlist %s...", name, wishlist_id)
        return cls.query.filter(cls.wishlist_id == wishlist_id, cls.name == name)

    @classmethod
    def remove_by_wishlist_id(cls, wishlist_id):
        """Removes all Items of a Wishlist from the database"""
        logger.info("Processing delete of all items for wishlist %s ...", wishlist_id)
        items = cls.query.filter(cls.wishlist_id == wishlist_id).all()
        for item in items:
            item.delete()
