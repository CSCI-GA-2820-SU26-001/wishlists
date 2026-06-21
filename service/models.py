"""
Models for Wishlist

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing"""


class Wishlist(db.Model):
    """
    Class that represents a Wishlist
    """

    ##################################################
    # Table Schema
    ##################################################
    __tablename__ = "wishlists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Wishlist {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Wishlist in the database
        """
        logger.info("Creating wishlist: %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error("Error creating wishlist: %s", self)
            raise DataValidationError(error) from error

    def update(self):
        """
        Updates a Wishlist in the database
        """
        logger.info("Saving wishlist: %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error("Error updating wishlist: %s", self)
            raise DataValidationError(error) from error

    def delete(self):
        """
        Removes a Wishlist from the database
        """
        logger.info("Deleting wishlist: %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error("Error deleting wishlist: %s", self)
            raise DataValidationError(error) from error

    def serialize(self):
        """
        Serializes a Wishlist into a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "customer_id": self.customer_id,
        }

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the wishlist data
        """
        try:
            self.name = data["name"]
            self.customer_id = data["customer_id"]
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
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """
        Returns all of the Wishlists in the database
        """
        logger.info("Processing all Wishlists")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """
        Finds a Wishlist by its ID
        """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """
        Returns all Wishlists with the given name

        Args:
            name (string): the name of the Wishlists you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()


# Temporary alias so old template code in routes.py does not break yet.
# We will remove this later after routes.py is updated to use Wishlist directly.
YourResourceModel = Wishlist