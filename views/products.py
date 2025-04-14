import streamlit as st
from typing import List, Dict
from models.cart import Cart

def render_products(products: List[Dict], cart: Cart):
    st.subheader("📦 Browse Products")
    
    for product in products:
        col1, col2 = st.columns([1, 3])
        with col1:
            if product.get('Image'):
                st.image(product['Image'], width=150)
        
        with col2:
            st.write(f"**{product['Product Name']}**")
            st.write(f"Price: ${product['Price']}")
            if product.get('Description'):
                st.write(product['Description'])
            
            col_qty, col_btn = st.columns([1, 2])
            with col_qty:
                qty = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    key=f"qty_{product['Product Name']}",
                    label_visibility="collapsed"
                )
            with col_btn:
                if st.button("Add to Cart", key=f"add_{product['Product Name']}"):
                    cart.add_item(st.session_state.cart_id, product['Product Name'], qty)
                    st.success(f"Added {qty} {product['Product Name']} to cart")
                    st.rerun()