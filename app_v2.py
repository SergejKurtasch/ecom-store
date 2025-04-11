import streamlit as st
import pandas as pd
from pymongo import MongoClient
import redis
import uuid
from typing import Dict, Any, List, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductStore:
    def __init__(
        self,
        mongo_url: str = "mongodb+srv://leonbittis:L4BzskbOs6W5IhJ6@ecommerce-cluster.bfh5qnh.mongodb.net/?retryWrites=true&w=majority",
        db_name: str = "eCommerce-Store",
        products_collection: str = "Products",
        orders_collection: str = "Orders",
        purchases_collection: str = "Purchases"
    ):
        try:
            self.client = MongoClient(mongo_url)
            self.db = self.client[db_name]
            self.products = self.db[products_collection]
            self.orders = self.db[orders_collection]
            self.purchases = self.db[purchases_collection]
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Fetch all products from the Products collection."""
        try:
            products = list(self.products.find({}, {"_id": 0}))
            logger.info(f"Fetched {len(products)} products")
            return products
        except Exception as e:
            logger.error(f"Failed to fetch products: {e}")
            return []

    def get_product_map(self) -> Dict[str, Any]:
        """Return a dictionary mapping product names to product details"""
        products = self.get_all_products()
        return {p['Product Name']: p for p in products}

    def save_order(self, order: Dict[str, Any]):
        """Save an order to the Orders collection."""
        try:
            order['created_at'] = datetime.utcnow()
            result = self.orders.insert_one(order)
            logger.info(f"Order saved with ID: {result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save order: {e}")
            return False

    def close(self):
        """Close the connection to the MongoDB client."""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

class Cart:
    def __init__(self, namespace: str = "cart"):
        redis_config = {
            'host': 'redis-15042.c328.europe-west3-1.gce.redns.redis-cloud.com',
            'port': 15042,
            'username': 'Martijn',
            'password': 'Ir0nh@ck',
            'db': 0,
            'decode_responses': True
        }
        
        try:
            self.r = redis.StrictRedis(**redis_config)
            self.r.ping()  # Test connection
            logger.info("Successfully connected to Redis")
            self.ns = namespace
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _key(self, cart_id: str) -> str:
        return f"{self.ns}:{cart_id}"

    def add_item(self, cart_id: str, product_name: str, qty: int = 1):
        """Add item to cart with quantity validation"""
        if qty <= 0:
            raise ValueError("Quantity must be positive")
            
        try:
            key = self._key(cart_id)
            current_qty = self.r.hget(key, product_name) or 0
            new_qty = int(current_qty) + qty
            self.r.hset(key, product_name, new_qty)
            logger.info(f"Added {qty} of {product_name} to cart {cart_id}")
        except Exception as e:
            logger.error(f"Failed to add item to cart: {e}")
            raise

    def update_item(self, cart_id: str, product_name: str, qty: int):
        """Update item quantity directly"""
        if qty < 0:
            raise ValueError("Quantity cannot be negative")
            
        try:
            key = self._key(cart_id)
            if qty == 0:
                self.r.hdel(key, product_name)
            else:
                self.r.hset(key, product_name, qty)
            logger.info(f"Updated {product_name} to {qty} in cart {cart_id}")
        except Exception as e:
            logger.error(f"Failed to update cart item: {e}")
            raise

    def get_items(self, cart_id: str) -> Dict[str, str]:
        """Get all items in cart"""
        try:
            return self.r.hgetall(self._key(cart_id))
        except Exception as e:
            logger.error(f"Failed to get cart items: {e}")
            return {}

    def get_cart_details(self, cart_id: str, product_map: Dict[str, Any]) -> Tuple[Dict[str, Dict], float]:
        """Return detailed cart contents with product info and total"""
        cart_items = self.get_items(cart_id)
        detailed_items = {}
        total = 0.0
        
        for name, qty in cart_items.items():
            if name in product_map:
                product = product_map[name]
                price = float(product['Price'])
                item_total = price * int(qty)
                detailed_items[name] = {
                    'quantity': int(qty),
                    'price': price,
                    'total': item_total,
                    'image': product.get('Image', '')
                }
                total += item_total
        
        return detailed_items, total

    def clear(self, cart_id: str):
        """Empty the cart"""
        try:
            self.r.delete(self._key(cart_id))
            logger.info(f"Cleared cart {cart_id}")
        except Exception as e:
            logger.error(f"Failed to clear cart: {e}")
            raise

def init_session():
    """Initialize session state variables"""
    if "cart_id" not in st.session_state:
        st.session_state.cart_id = str(uuid.uuid4())
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Home"

def render_navbar(cart_count: int):
    """Render the navigation bar"""
    col1, col2 = st.columns([4, 1])
    with col1:
        tabs = ["Home", "Products", "Recommendations", "Cart", "Checkout", "Order History"]
        st.session_state.current_tab = st.radio(
            "Navigation", 
            tabs,
            index=tabs.index(st.session_state.current_tab),
            horizontal=True,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown(f"""
        <div style="text-align: right; margin-bottom: 20px;">
            <span style="font-size: 24px;">🛒</span>
            <span style="background-color: red; color: white; 
                         border-radius: 50%; padding: 2px 8px; 
                         font-size: 14px; position: relative; top: -10px;">
                {cart_count}
            </span>
        </div>
        """, unsafe_allow_html=True)

def render_products(products: List[Dict], cart: Cart):
    """Render products page"""
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
                            "product": name,
                            "quantity": details['quantity'],
                            "price": details['price'],
                            "total": details['total']
                        } for name, details in cart_details.items()
                    ],
                    "total": total,
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

def render_order_history(product_store: ProductStore):
    """Render order history page"""
    st.subheader("📝 Your Order History")
    
    # Get email from session state if available
    user_email = st.session_state.get('user_email')
    
    if not user_email:
        st.warning("Please complete a checkout first to view your order history")
        return
    
    # Query orders by email instead of cart_id
    orders = list(product_store.orders.find({"customer.email": user_email}, {"_id": 0}).sort("created_at", -1))
    
    if not orders:
        st.warning("You haven't placed any orders yet.")
    else:
        for order in orders:
            with st.expander(f"Order #{order['cart_id'][:8]} - {order['status']} - {order['created_at'].strftime('%Y-%m-%d')}"):
                st.write(f"**Date:** {order['created_at'].strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Status:** {order['status']}")
                st.write(f"**Payment Method:** {order.get('payment_method', 'N/A')}")
                
                st.write("**Items:**")
                for item in order['items']:
                    st.write(f"- {item['product']}: {item['quantity']} x ${item['price']:.2f}")
                
                st.write(f"**Total:** ${order['total']:.2f}")
#Main app
def main():
    st.set_page_config(
        page_title="Mini E-Commerce Store",
        page_icon="🛒",
        layout="wide"
    )
    st.title("🛒 Mini E-Commerce Store")
    
    # Initialize session
    init_session()
    
    # Initialize services
    try:
        product_store = ProductStore()
        cart = Cart()
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        return
    
    # Load products
    products = product_store.get_all_products()
    if not products:
        st.warning("No products available in the database.")
        return
    
    product_map = product_store.get_product_map()
    
    # Get cart count for navbar
    cart_count = len(cart.get_items(st.session_state.cart_id))
    
    # Render navigation
    render_navbar(cart_count)
    
    # Render current tab
    if st.session_state.current_tab == "Home":
        st.subheader("Welcome to our store!")
        st.write("Explore products, add them to your cart, and get personalized recommendations.")
    
    elif st.session_state.current_tab == "Products":
        render_products(products, cart)
    
    elif st.session_state.current_tab == "Cart":
        render_cart(cart, product_map)
    
    elif st.session_state.current_tab == "Checkout":
        render_checkout(cart, product_store, product_map)
    
    elif st.session_state.current_tab == "Order History":
        render_order_history(product_store)

if __name__ == "__main__":
    main()