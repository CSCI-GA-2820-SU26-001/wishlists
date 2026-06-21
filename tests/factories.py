"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Wishlist


class WishlistFactory(factory.Factory):
    """Creates fake Wishlists"""

    class Meta:
        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"Wishlist {n}")
    customer_id = factory.Sequence(lambda n: n + 1000)



YourResourceModelFactory = WishlistFactory