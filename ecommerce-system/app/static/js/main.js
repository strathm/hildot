// Wait for the DOM to be fully loaded
$(document).ready(function () {

    // Cart functionality: Add to Cart
    $(".btn-add-to-cart").click(function (e) {
        e.preventDefault();
        
        let productId = $(this).data("product-id");
        let quantity = $("#quantity-" + productId).val() || 1;
        
        // Send an AJAX request to add item to the cart
        $.ajax({
            url: '/cart/add',
            method: 'POST',
            data: {
                product_id: productId,
                quantity: quantity,
                csrf_token: $("input[name='csrf_token']").val()
            },
            success: function(response) {
                if (response.success) {
                    // Update the cart count displayed in the navbar
                    $("#cart-count").text(response.cart_count);
                    alert("Product added to cart!");
                } else {
                    alert("Failed to add item to cart.");
                }
            },
            error: function() {
                alert("There was an error adding the item to the cart.");
            }
        });
    });

    // Handling quantity changes in the cart
    $(".cart-item-quantity").on("change", function () {
        let productId = $(this).data("product-id");
        let newQuantity = $(this).val();
        
        // Update the cart by sending the new quantity to the server
        $.ajax({
            url: '/cart/update',
            method: 'POST',
            data: {
                product_id: productId,
                quantity: newQuantity,
                csrf_token: $("input[name='csrf_token']").val()
            },
            success: function(response) {
                if (response.success) {
                    // Update cart total
                    $("#cart-total").text(response.cart_total);
                } else {
                    alert("Failed to update cart.");
                }
            },
            error: function() {
                alert("There was an error updating the cart.");
            }
        });
    });

    // Checkout function
    $("#checkout-btn").click(function (e) {
        e.preventDefault();

        let cartItems = $(".cart-item");

        if (cartItems.length === 0) {
            alert("Your cart is empty!");
            return;
        }

        // Confirm before proceeding to checkout
        let confirmCheckout = confirm("Are you sure you want to proceed to checkout?");
        if (confirmCheckout) {
            window.location.href = '/checkout';
        }
    });

    // Handling product quantity input (preventing negative or zero values)
    $(".product-quantity-input").on("input", function () {
        let value = $(this).val();
        if (value <= 0) {
            $(this).val(1); // Set the minimum quantity to 1
        }
    });

    // Toggle the visibility of the cart dropdown in the navbar
    $(".cart-dropdown-toggle").click(function () {
        $(".cart-dropdown").toggleClass("show");
    });

    // Handle feedback form submission
    $("#feedback-form").on("submit", function (e) {
        e.preventDefault();

        let productId = $("#product-id").val();
        let rating = $("input[name='rating']:checked").val();
        let comment = $("#comment").val();

        // Validate feedback form
        if (!rating || !comment) {
            alert("Please provide a rating and comment!");
            return;
        }

        $.ajax({
            url: '/feedback/' + productId,
            method: 'POST',
            data: {
                rating: rating,
                comment: comment,
                csrf_token: $("input[name='csrf_token']").val()
            },
            success: function(response) {
                if (response.success) {
                    alert("Thank you for your feedback!");
                    location.reload(); // Reload the page to show the new feedback
                } else {
                    alert("Failed to submit feedback.");
                }
            },
            error: function() {
                alert("There was an error submitting your feedback.");
            }
        });
    });

    // Dynamic low-stock alert (auto update as the page loads)
    function updateLowStockAlert() {
        $.ajax({
            url: '/admin/low-stock-alert',
            method: 'GET',
            success: function(response) {
                if (response.products.length > 0) {
                    $(".low-stock-alert").show();
                    response.products.forEach(function (product) {
                        let alertMessage = `${product.name} is running low on stock! Only ${product.quantity} left.`;
                        $(".low-stock-alert").append(`<div class="alert alert-warning">${alertMessage}</div>`);
                    });
                } else {
                    $(".low-stock-alert").hide();
                }
            }
        });
    }

    // Call the function to update low-stock alerts
    updateLowStockAlert();

});

// Scroll to top functionality
function scrollToTop() {
    $('html, body').animate({
        scrollTop: 0
    }, 500);
}

// Add event listener to "back to top" button
$("#back-to-top-btn").click(function () {
    scrollToTop();
});
