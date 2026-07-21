Feature: Wishlist Management
    As a customer
    I need to manage wishlists
    So that I can save and remove items I want to buy later

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

    Scenario: Delete an existing wishlist
        Given the wishlist service is running
        And a wishlist exists with customer id "1002", name "Delete Me", and description "Temporary wishlist"
        When I delete the wishlist
        Then the response status code should be 204
        And the wishlist should no longer be available

    Scenario: Read an existing wishlist
        Given the wishlist service is running
        And a wishlist exists with customer id "2001", name "Read Wishlist", and description "Wishlist to read"
        When I request the wishlist
        Then the response status code should be 200
        And the response should contain customer id "2001"
        And the response should contain name "Read Wishlist"
        And the response should contain description "Wishlist to read"

    Scenario: List all wishlists
        Given the wishlist service is running
        And a wishlist exists with customer id "2002", name "List Wishlist One", and description "First wishlist to list"
        And a wishlist exists with customer id "2003", name "List Wishlist Two", and description "Second wishlist to list"
        When I request all wishlists
        Then the response status code should be 200
        And the response list should contain wishlist named "List Wishlist One"
        And the response list should contain wishlist named "List Wishlist Two"

    Scenario: Query wishlists by customer id
        Given the wishlist service is running
        Given multiple wishlists exist
        When I query wishlists with customer id "1001"
        Then the response status code should be 200
        And only wishlists for customer id "1001" are returned