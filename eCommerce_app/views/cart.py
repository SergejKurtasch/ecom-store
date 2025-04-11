import streamlit as st
from typing import Dict, Any
from models.cart import Cart

def render_cart(cart: Cart, product_map: Dict[str, Any]):
    """Render shopping cart page"""
    st.subheader("🛒 Your Shopping Cart")
    
    cart_details, total = cart.get_cart_details(st.session_state.cart_id, product_map)
    
    if not cart_details:
        st.warning("Your cart is empty.")
        return
    
    # Create a copy of the cart details to track changes
    updated_cart = cart_details.copy()
    
    for product_name, details in cart_details.items():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        with col1:
            st.write(f"**{product_name}**")
            if details['image']:
                st.image(details['image'], width=100)
        
        with col2:
            st.write(f"${details['price']:.2f}")
        
        with col3:
            # Use a callback to update the cart when quantity changes
            def update_qty(pn=product_name):
                new_qty = st.session_state[f"qty_{pn}"]
                if new_qty != cart_details[pn]['quantity']:
                    cart.update_item(st.session_state.cart_id, pn, new_qty)
                    
            
            new_qty = st.number_input(
                "Quantity",
                min_value=1,
                max_value=100,
                value=details['quantity'],
                key=f"qty_{product_name}",
                label_visibility="collapsed",
                on_change=update_qty
            )
            updated_cart[product_name]['quantity'] = new_qty
        
        with col4:
            item_total = details['price'] * new_qty
            st.write(f"${item_total:.2f}")
            updated_cart[product_name]['total'] = item_total
        
        with col5:
            if st.button("❌", key=f"remove_{product_name}"):
                cart.update_item(st.session_state.cart_id, product_name, 0)
                st.rerun()
        
        st.write("---")
    
    # Calculate the updated total
    total = sum(item['total'] for item in updated_cart.values())
    st.markdown(f"**Total: ${total:.2f}**", unsafe_allow_html=True)
    
    if st.button("Proceed to Checkout", type="primary"):
        st.session_state.current_tab = "Checkout"
        st.rerun()