import streamlit as st
import uuid  
from typing import Dict, Any
from datetime import datetime
from models.cart import Cart
from models.product_store import ProductStore

def render_checkout(cart: Cart, product_store: ProductStore, product_map: Dict[str, Any]):
    """Render checkout page"""
    st.subheader("💳 Checkout")
    
    cart_details, total = cart.get_cart_details(st.session_state.cart_id, product_map)
    
    if not cart_details:
        st.warning("Your cart is empty. Add some products before checkout.")
        st.session_state.current_tab = "Products"
        st.rerun()
        return
    
    with st.form("checkout_form"):
        # Order Summary
        st.write("### Order Summary")
        for product_name, details in cart_details.items():
            st.write(f"- {product_name}: {details['quantity']} x ${details['price']:.2f} = ${details['total']:.2f}")
        st.write(f"**Total: ${total:.2f}**")
        
        # Customer Information
        st.write("### Shipping Information")
        name = st.text_input("Full Name*")
        email = st.text_input("Email*")
        address = st.text_area("Shipping Address*")
        
        # Payment Method
        st.write("### Payment Method")
        payment_method = st.radio(
            "Select payment method",
            ["Credit Card", "PayPal", "Bank Transfer"],
            horizontal=True
        )
        
        # Terms and Conditions
        agree = st.checkbox("I agree to the terms and conditions*")
        
        # Submit Button
        submitted = st.form_submit_button("Place Order", type="primary")
        
        if submitted:
            if not all([name, email, address, agree]):
                st.error("Please fill all required fields (*)")
            else:
                # Store email in session state for order history
                st.session_state.user_email = email
                
                order  = {
                    "cart_id": st.session_state.cart_id,
                    "customer": {
                        "name": name,
                        "email": email,
                        "address": address
                    },
                    "payment_method": payment_method,
                    "items": [
                        {    
                            "product_id": product_map[product_name].get("ID"), # Using the numeric ID
                            "product_name": product_name,
                            "quantity": details['quantity'],
                            "category": product_map[product_name].get("Category"),
                            "quantity": details['quantity'],
                            "unit_price": float(details['price']),
                            "total_price": float(details['total']),
                            "image_url": product_map[product_name].get("Image")
    
                        } for product_name, details in cart_details.items()
                    ],
                    "order_total": float(total),
                    "status": "Pending",
                    "created_at": datetime.utcnow()
                }
                
                if product_store.save_order(order):
                    cart.clear(st.session_state.cart_id)
                    st.session_state.cart_id = str(uuid.uuid4())
                    st.success("Order placed successfully!")
                    st.balloons()
                    st.session_state.current_tab = "Order History"
                    st.rerun()
                else:
                    st.error("Failed to place order. Please try again.")