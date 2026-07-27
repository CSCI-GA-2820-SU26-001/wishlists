$(function () {

    let current_wishlist_id = null;

    const BASE_URL = "api/wishlists"

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the wishlist form with data from the response
    function update_wishlist_data(res) {
        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.name);
        $("#customer_id").val(res.customer_id);
        $("#wishlist_description").val(res.description);
    }

    /// Clears all wishlist form fields
    function clear_wishlist_data() {
        $("#wishlist_name").val("");
        $("#customer_id").val("");
        $("#wishlist_description").val("");
    }

    // Updates the item form with data from the response
    function update_item_data(res) {
        $("#item_id").val(res.id);
        $("#item_name").val(res.name);
        $("#item_quantity").val(res.quantity);
    }

    /// Clears all item form fields
    function clear_item_data() {
        $("#item_name").val("");
        $("#item_quantity").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // Sets active wishlist whenever a wishlist is retrieved/selected,
    function set_active_wishlist(wishlist_id, wishlist_name) {
        current_wishlist_id = wishlist_id;
        $("#active_wishlist_name").text(wishlist_name || "(unnamed)");
        $("#active_wishlist_id").text(wishlist_id);
    }

    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#wishlist_name").val();
        let cid = parseInt($("#customer_id").val(),10)
        let description = $("#wishlist_description").val();

        let data = {
            "name": name,
            "customer_id": cid,
            "description": description
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `${BASE_URL}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_wishlist_data(res)
            flash_message("Success")
            set_active_wishlist(res.id, res.name)
        });

        ajax.fail(function(res){
            let msg = res.responseJSON.message;
            if (res.responseJSON.errors) {
                msg += ": " + JSON.stringify(res.responseJSON.errors);
            }
            flash_message(msg);
        });

        // ajax.fail(function(res){
        //     flash_message(res.responseJSON.message)
        // });
    });


    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#update-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        let name = $("#wishlist_name").val();
        let cid = parseInt($("#customer_id").val(),10)
        let description = $("#wishlist_description").val();

        let data = {
            "name": name,
            "customer_id": cid,
            "description": description
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `${BASE_URL}/${wishlist_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_wishlist_data(res)
            flash_message("Success")
            set_active_wishlist(res.id, res.name)
            $("#search-btn").click();
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Wishlist
    // ****************************************

    $("#retrieve-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}/${wishlist_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_wishlist_data(res)
            flash_message("Success")
            set_active_wishlist(res.id, res.name)
        });

        ajax.fail(function(res){
            clear_wishlist_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `${BASE_URL}/${wishlist_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_wishlist_data()
            flash_message("Wishlist has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        $("#flash_message").empty();
        clear_wishlist_data()
    });

    // ****************************************
    // Search for a Wishlist
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#wishlist_name").val();
        let cid = parseInt($("#customer_id").val(),10)
        let description = $("#wishlist_description").val();

        let params = [];

        if (name) {
            params.push('name=' + encodeURIComponent(name));
        }
        if (cid) {
            params.push('customer_id=' + encodeURIComponent(cid));
        }

        let queryString = params.join('&');

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Customer ID</th>'
            table += '</tr></thead><tbody>'
            let firstWishlist = "";
            for(let i = 0; i < res.length; i++) {
                let wishlist = res[i];
                table +=  `<tr id="row_${i}"><td>${wishlist.id}</td><td>${wishlist.name}</td><td>${wishlist.customer_id}</td></tr>`;
                if (i == 0) {
                    firstWishlist = wishlist;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstWishlist != "") {
                update_wishlist_data(firstWishlist)
                set_active_wishlist(firstWishlist.id, firstWishlist.name)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Create an Item
    // ****************************************

    $("#item-create-btn").click(function () {
        if (!current_wishlist_id) {
            flash_message("Please select a Wishlist first");
            return;
        }
        let data = {
            wishlist_id: current_wishlist_id,
            name: $("#item_name").val(),
            quantity: parseInt($("#item_quantity").val(),10),
        };

        $.ajax({
            type: "POST",
            url: `${BASE_URL}/${current_wishlist_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        }).done(function (res) {
            flash_message("Item created");
        }).fail(function (res) {
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Update an Item
    // ****************************************

    $("#item-update-btn").click(function () {
        if (!current_wishlist_id) {
            flash_message("Please select a Wishlist first");
            return;
        }
        let item_id = $("#item_id").val();
        let name = $("#item_name").val();
        let quantity = parseInt($("#item_quantity").val(),10);

        let data = {
            wishlist_id: current_wishlist_id,
            name: name,
            quantity: quantity,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `${BASE_URL}/${current_wishlist_id}/items/${item_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_item_data(res)
            flash_message("Success")
            $("#item-search-btn").click();
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });
    
    // ****************************************
    // Retrieve an Item
    // ****************************************

    $("#item-retrieve-btn").click(function () {
        if (!current_wishlist_id) {
            flash_message("Please select a Wishlist first");
            return;
        }
        let item_id = parseInt($("#item_id").val(),10);

        $.ajax({
            type: "GET",
            url: `${BASE_URL}/${current_wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        }).done(function (res) {
            // NEW: populate item form fields
            $("#item_name").val(res.name);
            $("#item_quantity").val(res.quantity);
            flash_message("Success");
        }).fail(function (res) {
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Delete an Item
    // ****************************************

    $("#item-delete-btn").click(function () {
        let item_id = $("#item_id").val();
        $.ajax({
            type: "DELETE",
            url: `${BASE_URL}/${current_wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        }).done(function (res) {
            flash_message("Item deleted");
        }).fail(function (res) {
            flash_message("Server error!");
        });
    });

    // ****************************************
    // Clear the item form
    // ****************************************

    $("#item-clear-btn").click(function () {
        $("#item_id").val("");
        $("#flash_message").empty();
        clear_item_data()
    });

    // ****************************************
    // Search for an Item
    // ****************************************

    $("#item-search-btn").click(function () {
        if (!current_wishlist_id) {
            flash_message("Please select a Wishlist first");
            return;
        }
        let name = $("#item_name").val();
        let params = [];
        if (name) {
            params.push('name=' + encodeURIComponent(name));
        }
        let queryString = params.join('&');
        let url = `${BASE_URL}/${current_wishlist_id}/items`;
        if (queryString) {
            url += '?' + queryString;
        }
        $.ajax({
            type: "GET",
            url: url,
            contentType: "application/json",
        }).done(function (res) {
            $("#item_search_results table tbody").remove();
            let table = '<tbody>';
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr><td>${item.id}</td><td>${item.name}</td><td>${item.quantity}</td></tr>`;
            }
            table += '</tbody>';
            $("#item_search_results table").append(table);
            flash_message("Success");
        }).fail(function (res) {
            flash_message(res.responseJSON.message);
        });
    });

})
