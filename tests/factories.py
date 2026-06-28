"""
Test Factory to make fake objects for testing
"""

from factory import Factory, Faker, SubFactory, Sequence, post_generation
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from service.models import Wishlist, Item


class WishlistFactory(Factory):
    """Creates fake Wishlists"""

    class Meta:
        """Factory metadata: binds to the Wishlist model."""

        model = Wishlist

    id = Sequence(lambda n: n)
    name = Sequence(lambda n: f"Wishlist {n}")
    customer_id = FuzzyInteger(1, 1000)
    description = FuzzyChoice(choices=["Some descriptions ...", ""])

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the addresses list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(Factory):
    """Creates fake Items"""

    class Meta:
        """Factory metadata: binds to the Item model."""

        model = Item

    id = Sequence(lambda n: n)
    wishlist_id = None
    name = Faker("word")
    quantity = FuzzyInteger(1, 100)
    wishlist = SubFactory(WishlistFactory)
