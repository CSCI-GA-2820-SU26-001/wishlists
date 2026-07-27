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
Wishlist Service with Swagger

Paths:
------
GET / - Displays a UI for Selenium testing
GET /health - Returns health status

GET /wishlists - Returns a list all of the Wishlists
GET /wishlists/{wishlist_id} - Returns the Wishlist with a given wishlist_id number
POST /wishlists - creates a new Wishlist record in the database
PUT /wishlists/{wishlist_id} - updates a Wishlist record in the database
DELETE /wishlists/{wishlist_id} - deletes a Wishlist record in the database
DELETE /wishlists - deletes all Wishlist records in the database (for testing only)

GET /wishlists/{wishlist_id}/items - Returns a list all of the Items in a Wishlist
GET /wishlists/{wishlist_id}/items/{item_id} - Returns the Item with a given item_id number
POST /wishlists/{wishlist_id}/items - creates a new Item record in the database
PUT /wishlists/{wishlist_id}/items/{item_id} - updates a Item record in the database
DELETE /wishlists/{wishlist_id}/items/{item_id} - deletes a Item record in the database

PUT /wishlists/{wishlist_id}/items/clear - deletes all items in a wishlist
"""

from flask import jsonify, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse
from service.models import Wishlist, Item
from service.common import status  # HTTP Status Codes

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Wishlists Demo REST API Service",
    description="This is a sample server Wishlists server.",
    default="wishlists",
    default_label="Wishlists service operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    # authorizations=authorizations,
    prefix="/api",
)


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


@app.route("/health")
def health():
    """Health Status"""
    return jsonify(status="OK"), status.HTTP_200_OK


# Define the model so that the docs reflect what can be sent

item_create_model = api.model(
    "ItemCreate",
    {
        "wishlist_id": fields.Integer(
            required=False,
            description="The wishlist id of the Wishlist (datatype: int)",
        ),
        "name": fields.String(required=True, description="The name of the Item"),
        "quantity": fields.Integer(
            required=True,
            description="The quantity of the item (datatype: int)",
        ),
        # pylint: disable=protected-access
    },
)

item_model = api.inherit(
    "ItemModel",
    item_create_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The unique item id assigned internally by service",
        ),
    },
)

wishlist_create_model = api.model(
    "WishlistCreate",
    {
        "name": fields.String(required=True, description="The name of the Wishlist"),
        "customer_id": fields.Integer(
            required=True,
            description="The customer id of the Wishlist (datatype: int)",
        ),
        # pylint: disable=protected-access
        "description": fields.String(
            required=False, description="The description of the Wishlist"
        ),
    },
)

wishlist_model = api.inherit(
    "WishlistModel",
    wishlist_create_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The unique wishlist id assigned internally by service",
        ),
        "items": fields.List(fields.Nested(item_model), readonly=True),
    },
)

# query string arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument(
    "name", type=str, location="args", required=False, help="List Wishlists by name"
)
wishlist_args.add_argument(
    "customer_id",
    type=int,
    location="args",
    required=False,
    help="List Wishlists by customer id",
)

item_args = reqparse.RequestParser()
item_args.add_argument(
    "name", type=str, location="args", required=False, help="List Items by name"
)


######################################################################
#  PATH: /wishlists/{wishlist_id}
######################################################################
@api.route("/wishlists/<int:wishlist_id>")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistResource(Resource):
    """
    WishlistResource class

    Allows the manipulation of a single Wishlist
    GET /wishlist{id} - Returns a Wishlist with the id
    PUT /wishlist{id} - Update a Wishlist with the id
    DELETE /wishlist{id} -  Deletes a Wishlist with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("get_wishlist")
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieve a single Wishlist

        This endpoint will return a Wishlist based on it's id
        """
        app.logger.info("Request to Retrieve a wishlist with id [%s]", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING WISHLIST
    # ------------------------------------------------------------------
    @api.doc("update_wishlist")
    @api.response(404, "Wishlist not found")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Update a Wishlist

        This endpoint will update a Wishlist based the body that is posted
        """
        app.logger.info("Request to Update a wishlist with id [%s]", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        wishlist.deserialize(data)
        wishlist.id = wishlist_id
        wishlist.update()
        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("delete_wishlist")
    @api.response(204, "Wishlist deleted")
    def delete(self, wishlist_id):
        """
        Delete a Wishlist

        This endpoint will delete a Wishlist based the id specified in the path
        """
        app.logger.info("Request to Delete a wishlist with id [%s]", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
            app.logger.info("Wishlist with id [%s] was deleted", wishlist_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists
######################################################################
@api.route("/wishlists", strict_slashes=False)
class WishlistCollection(Resource):
    """Handles all interactions with collections of Wishlists"""

    # ------------------------------------------------------------------
    # LIST ALL WISHLISTS
    # ------------------------------------------------------------------
    @api.doc("list_wishlists")
    @api.expect(wishlist_args, validate=True)
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """Returns all of the Wishlists"""
        app.logger.info("Request to list Wishlists...")
        wishlists = []
        args = wishlist_args.parse_args()
        if args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            wishlists = Wishlist.find_by_name(args["name"])
        elif args["customer_id"]:
            app.logger.info("Filtering by customer id: %s", args["customer_id"])
            wishlists = Wishlist.find_by_customer_id(args["customer_id"])
        else:
            app.logger.info("Returning unfiltered list.")
            wishlists = Wishlist.all()

        wishlists = list(wishlists)
        app.logger.info("[%s] Wishlists returned", len(wishlists))
        results = [wishlist.serialize() for wishlist in wishlists]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW WISHLIST
    # ------------------------------------------------------------------
    @api.doc("create_wishlist")
    @api.response(400, "The posted data was not valid")
    @api.expect(wishlist_create_model, validate=True)
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Creates a Wishlist
        This endpoint will create a Wishlist based the data in the body that is posted
        """
        app.logger.info("Request to Create a Wishlist")
        wishlist = Wishlist()
        app.logger.debug("Payload = %s", api.payload)
        wishlist.deserialize(api.payload)
        wishlist.create()
        app.logger.info("Wishlist with new id [%s] created!", wishlist.id)
        location_url = api.url_for(
            WishlistResource, wishlist_id=wishlist.id, _external=True
        )
        return wishlist.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    # ------------------------------------------------------------------
    # DELETE ALL WISHLISTS (for testing only)
    # ------------------------------------------------------------------
    @api.doc("delete_all_wishlists")
    @api.response(204, "All Wishlists deleted")
    def delete(self):
        """
        Delete all Wishlists

        This endpoint will delete all Wishlists only if the system is under test
        """
        app.logger.info("Request to Delete all wishlists...")
        if "TESTING" in app.config and app.config["TESTING"]:
            Wishlist.remove_all()
            app.logger.info("Removed all Wishlists from the database")
        else:
            app.logger.warning("Request to clear database while system not under test")

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists/{wishlist_id}/items/{item_id}
######################################################################
@api.route("/wishlists/<int:wishlist_id>/items/<item_id>")
@api.param("wishlist_id", "The Wishlist identifier")
@api.param("item_id", "The Item identifier")
class ItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Item
    GET /wishlists/{wishlist_id}items/{item_id} - Returns a Item with the id
    PUT /wishlists/{wishlist_id}items/{item_id} - Update a Item with the id
    DELETE /wishlists/{wishlist_id}items/{item_id} -  Deletes a Item with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("get_item")
    @api.response(404, "Wishlist not found")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, wishlist_id, item_id):
        """
        Retrieve a single Item

        This endpoint will return a Item based on it's id
        """
        app.logger.info(
            "Request to read item %s from wishlist %s",
            item_id,
            wishlist_id,
        )
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        item = Item.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found.",
            )
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ITEM
    # ------------------------------------------------------------------
    @api.doc("update_item")
    @api.response(404, "Wishlist not found")
    @api.response(404, "Item not found")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, wishlist_id, item_id):
        """
        Update a Item

        This endpoint will update a Item based the body that is posted
        """
        app.logger.info(
            "Request to update item %s from wishlist %s",
            item_id,
            wishlist_id,
        )
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        item = Item.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        item.deserialize(data)
        item.id = item_id
        item.update()
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_item")
    @api.response(204, "Item deleted")
    def delete(self, wishlist_id, item_id):
        """
        Delete a Item

        This endpoint will delete a Item based the id specified in the path
        """
        app.logger.info(
            "Request to delete item %s from wishlist %s",
            item_id,
            wishlist_id,
        )
        # See if the item exists and delete it if it does
        item = Item.find(item_id)
        if item:
            item.delete()
            app.logger.info("Item with id [%s] was deleted", item_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists/{wishlist_id}/items
######################################################################
@api.route("/wishlists/<int:wishlist_id>/items", strict_slashes=False)
@api.param("wishlist_id", "The Wishlist identifier")
class ItemCollection(Resource):
    """Handles all interactions with collections of Items"""

    # ------------------------------------------------------------------
    # LIST ALL ITEMS
    # ------------------------------------------------------------------
    @api.doc("list_items")
    @api.response(404, "Wishlist not found")
    @api.expect(item_args, validate=True)
    @api.marshal_list_with(item_model)
    def get(self, wishlist_id):
        """Returns all of the Items in the Wishlist with wishlist_id"""
        app.logger.info("Request to list items for wishlist %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        items = []
        args = item_args.parse_args()
        if args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            items = list(Item.find_by_wishlist_and_name(wishlist_id, args["name"]))
        else:
            app.logger.info("Returning unfiltered list.")
            items = wishlist.items

        app.logger.info("[%s] Items returned", len(items))
        results = [item.serialize() for item in items]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW ITEM
    # ------------------------------------------------------------------
    @api.doc("create_item")
    @api.response(404, "Wishlist not found")
    @api.response(400, "The posted data was not valid")
    @api.expect(item_create_model, validate=True)
    @api.marshal_with(item_model, code=201)
    def post(self, wishlist_id):
        """
        Creates an Item
        This endpoint will create a Item based the data in the body that is posted
        """
        app.logger.info("Request to Create a Item to wishlist %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        item = Item()
        app.logger.debug("Payload = %s", api.payload)
        item.deserialize(api.payload)
        item.wishlist_id = wishlist_id
        item.create()
        app.logger.info("Item with new id [%s] created!", item.id)
        location_url = api.url_for(
            ItemResource, wishlist_id=wishlist.id, item_id=item.id, _external=True
        )
        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /wishlists/{wishlist_id}/items/clear
######################################################################
@api.route("/wishlists/<int:wishlist_id>/items/clear")
@api.param("wishlist_id", "The Wishlist identifier")
class ClearItemsResource(Resource):
    """Clear Items actions on a Wishlist"""

    @api.doc("clear_items")
    @api.response(404, "Wishlist not found")
    @api.response(204, "All Items of a wishlist deleted")
    def put(self, wishlist_id):
        """
        Clear items

        This endpoint will clear all items from a wishlist
        """
        app.logger.info("Request to clear items from wishlist %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        Item.remove_by_wishlist_id(wishlist_id)
        app.logger.info("Removed all Items from the wishlist %s", wishlist_id)
        return "", status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
