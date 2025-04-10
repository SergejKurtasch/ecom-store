import streamlit as st 
import pandas as pd
from pymongo import MongoClient 
import redis 
import uuid
#from typing import Dict, Any, List

# Neo4j imports
from neo4j import GraphDatabase  

class Cart:
    def __init__(self, namespace: str = "cart"):
        self.r = redis.StrictRedis(
            host='redis-15042.c328.europe-west3-1.gce.redns.redis-cloud.com',
            port=15042,
            username='Martijn',
            password='Ir0nh@ck',
            db=0,
            decode_responses=True
            )
        self.ns = namespace

    def _key(self, cart_id: str) -> str:
        return f"{self.ns}:{cart_id}"

    def add_item(self, cart_id: str, product_name: str, qty: int = 1):
        key = self._key(cart_id)
        self.r.hincrby(key, product_name, qty)

    def remove_item(self, cart_id, product_name, qty = -1):
        key = self._key(cart_id)
        self.r.hincrby(key, product_name, qty)

    def get_items(self, cart_id: str):
        return self.r.hgetall(self._key(cart_id))

    def clear(self, cart_id: str):
        self.r.delete(self._key(cart_id))

def get_mongo_collection():
    client = MongoClient("mongodb+srv://leonbittis:L4BzskbOs6W5IhJ6@ecommerce-cluster.bfh5qnh.mongodb.net/?retryWrites=true&w=majority")
    db = client['eCommerce-Store']
    collection = db['Products'] 
    return  collection

# App setup
def main():
    st.set_page_config(page_title="Mini E‑Commerce Store", layout="wide")
    st.title("🛒 Mini E‑Commerce Store")

    # Initialize session cart_id
    if "cart_id" not in st.session_state:
        st.session_state.cart_id = str(uuid.uuid4())

    cart = Cart()
        # Fetch products from MongoDB
    products = list(get_mongo_collection().find({}))  # fetch all products from your collection
    if not products:
        st.warning("No products available in the database.")
        return

    # Navigation
    col1, col2 = st.columns([4,1])
    with col1:
        tab = st.radio("Navigation", ["Home", "Products", "Recommendations", "Cart", "Checkout"], horizontal=True)
    cart_count = len(cart.get_items(5))
    cart_icon = f'<a href="https://www.google.com/search?q=etest&oq=etest&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIMCAEQIxgnGIAEGIoFMgwIAhAjGCcYgAQYigUyBwgDEAAYgAQyBwgEEC4YgAQyDQgFEC4YxwEY0QMYgAQyDQgGEC4YxwEY0QMYgAQyDQgHEC4YxwEY0QMYgAQyBwgIEAAYgAQyDQgJEC4YxwEY0QMYgATSAQc3MTJqMGo5qAIAsAIB&sourceid=chrome&ie=UTF-8" style="text-decoration: none;">🛒</a>'
    with col2:
        st.markdown(f"""
        <div style="text-align: right; margin-bottom: 20px;">
            <span style="font-size: 24px;">{cart_icon}</span>
            <span style="background-color: red; color: white; 
                        border-radius: 50%; padding: 2px 8px; 
                        font-size: 14px; position: relative; top: -10px;">
                {cart_count}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Pages
    if tab == "Home":
        st.subheader("Welcome to our store!")
        st.write("Explore products, add them to your cart, and get personalized recommendations.")

    elif tab == "Products":
        st.subheader("📦 Browse Products")
        for product in products:
            st.write(f"**{product['Product Name']}** - ${product['Price']}")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image("https://via.placeholder.com/150", width=100)  # You can update this with product image URL
            with col2:
                if st.button("Add to Cart", key=f"add_{product['Product Name']}"):
                    cart.add_item(st.session_state.cart_id,product, product['name'], product['price'])
                    st.success(f"{product['Product Name']} added to cart.")

    elif tab == "Recommendations":
        st.subheader("🧠 Recommended for You")
        st.info("Here we’ll show similar items from Neo4j + Redis.")

    elif tab == "Cart":
        st.subheader("🛒 Your Shopping Cart")

        data = cart.get_items(1) # shuold be st.session_state.cart_id isntead of 5

        items = {}
        # Group data by item
        for key, value in data.items():
            name, attr = key.split(':')
            items.setdefault(name, {})[attr] = float(value)

        # Calculate totals
        for item, details in items.items():
             total = details['price'] * details['quantity']

        if len(data) == 0:
            st.warning("Your cart is empty.")
        else:
            for item in items:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                with col1:
                    st.write(item)
                with col2:
                    st.write(f"${items[item]['price']}")
                with col3:
                    st.write(f"${items[item]['quantity']}")
                with col4:
                    if st.button(f"Remove {item}"):
                        pass # to add remove when hash structure is set
            st.markdown(f"**Total: ${total}**")

    elif tab == "Checkout":
        st.subheader("💳 Checkout")
        if st.session_state.cart:
            st.success("Thank you for your purchase! (This will be stored in MongoDB later.)")
            if st.button("Place Order"):
                # Future: send to MongoDB
                st.session_state.cart.clear()
                st.experimental_rerun()
        else:
            st.warning("Cart is empty.")

if __name__ == "__main__":
    main()