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
Wishlist Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Wishlist
"""

from flask import jsonify, request, abort, url_for
from flask import current_app as app  # Import Flask application
from service.models import Wishlist, Item
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Wishlists Service",
            version="1.0.0",
            list_url="/wishlists",
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(status="OK"), status.HTTP_200_OK


@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Creates a Wishlist
    This endpoint will create a Wishlist based the data in the body that is posted
    """
    app.logger.info("Creating a wishlist ...")
    check_content_type("application/json")

    # Create the wishlist
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()

    # Create a message to return
    message = wishlist.serialize()
    location_url = url_for("get_wishlist", wishlist_id=wishlist.id, _external=True)

    return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# LIST WISHLISTS
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """Returns all of the Wishlists"""
    app.logger.info("Request to list Wishlists")

    wishlists = Wishlist.all()
    results = [wishlist.serialize() for wishlist in wishlists]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ AN ITEM
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["GET"])
def get_item(wishlist_id, item_id):
    """Read an Item"""

    app.logger.info(
        "Request to read item %s from wishlist %s",
        item_id,
        wishlist_id,
    )

    wishlist = Wishlist.find(wishlist_id)

    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, "Wishlist not found")

    item = Item.find(item_id)

    if not item or item.wishlist_id != wishlist_id:
        abort(status.HTTP_404_NOT_FOUND, "Item not found")

    return item.serialize(), status.HTTP_200_OK


######################################################################
# ADD AN ITEM TO A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["POST"])
def create_item(wishlist_id):
    """Add an Item to a Wishlist"""

    app.logger.info("Adding item to wishlist %s", wishlist_id)
    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)

    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, "Wishlist not found")

    data = request.get_json()
    data["wishlist_id"] = wishlist_id

    # Create the item
    item = Item()
    item.deserialize(data)
    item.create()

    # Create a message to return
    message = item.serialize()
    location_url = url_for(
        "get_item", wishlist_id=wishlist.id, item_id=item.id, _external=True
    )

    return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# READ WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlist(wishlist_id):
    """Returns a single Wishlist"""
    app.logger.info("Request to read Wishlist with id: %s", wishlist_id)

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
# LIST ITEMS IN A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["GET"])
def list_items(wishlist_id):
    """List all items in a wishlist"""

    app.logger.info("Request to list items for wishlist %s", wishlist_id)

    wishlist = Wishlist.find(wishlist_id)

    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, "Wishlist not found")

    items = []

    for item in wishlist.items:
        items.append(item.serialize())

    return items, status.HTTP_200_OK


######################################################################
# UPDATE AN ITEM
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["PUT"])
def update_item(wishlist_id, item_id):
    """Update an Item in a Wishlist"""

    app.logger.info(
        "Request to update item %s from wishlist %s",
        item_id,
        wishlist_id,
    )

    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)

    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, "Wishlist not found")

    item = Item.find(item_id)

    if not item or item.wishlist_id != wishlist_id:
        abort(status.HTTP_404_NOT_FOUND, "Item not found")

    data = request.get_json()
    data["wishlist_id"] = wishlist_id

    item.deserialize(data)
    item.update()

    return item.serialize(), status.HTTP_200_OK


######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(wishlist_id, item_id):
    """
    Delete an Item

    This endpoint will delete an Item based the id specified in the path
    """
    app.logger.info(
        "Request to delete Item %s for Wishlist id: %s", (item_id, wishlist_id)
    )

    # See if the item exists and delete it if it does
    item = Item.find(item_id)
    if item:
        item.delete()
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# DELETE WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlist(wishlist_id):
    """Delete a Wishlist"""
    app.logger.info("Request to delete Wishlist with id: %s", wishlist_id)

    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
def update_wishlist(wishlist_id):
    """Update a Wishlist"""
    app.logger.info("Request to update Wishlist with id: %s", wishlist_id)

    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    wishlist.deserialize(request.get_json())
    wishlist.id = wishlist_id
    wishlist.update()

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )
