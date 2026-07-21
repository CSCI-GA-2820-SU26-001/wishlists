Feature: Wishlist Management
    As a customer
    I need to create wishlists
    So that I can save items I want to buy later

    Scenario: Create a new wishlist
        Given the wishlist service is running
        When I create a wishlist with customer id "1001", name "Birthday Wishlist", and description "Birthday gift ideas"
        Then the response status code should be 201
        And the response should contain customer id "1001"
        And the response should contain name "Birthday Wishlist"
        And the response should contain description "Birthday gift ideas"

    Scenario: Update an existing wishlist
        Given the wishlist service is running
        Given a wishlist exists
        When I update the wishlist with customer id "1002", name "Updated Wishlist", and description "Updated description"
        Then the response status code should be 200
        And the response should contain customer id "1002"
        And the response should contain name "Updated Wishlist"
        And the response should contain description "Updated description"