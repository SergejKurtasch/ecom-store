import streamlit as st
import uuid
import logging
from datetime import datetime
from models.product_store import ProductStore
from models.cart import Cart
from views.navbar import render_navbar
from views.products import render_products
from views.cart import render_cart
from views.checkout import render_checkout
from views.order_history import render_order_history
from config import TABS

# from neo4j import GraphDatabase
# from views.suggestions_neo4j_test3 import get_product_recommendation

# Neo4j Connection - Replace with your credentials
NEO4J_URI = "neo4j+s://5e56b2da.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "h-jFkG_yO2J_fyusi1QPy6l80eSD_o-dD6tLqC20ePM"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_session():
    """Initialize session state variables"""
    if "cart_id" not in st.session_state:
        st.session_state.cart_id = str(uuid.uuid4())
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Home"

def render_home():
    """Render home page"""
    st.subheader("Welcome to our store!")
    st.write("Explore products, add them to your cart, and get personalized recommendations.")

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
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        st.error("Failed to initialize application services")
        return
    
    # Load products
    try:
        products = product_store.get_all_products()
        if not products:
            st.warning("No products available in the database.")
            return
        product_map = product_store.get_product_map()
    except Exception as e:
        logger.error(f"Failed to load products: {e}")
        st.error("Failed to load product catalog")
        return
    
    # Get cart count for navbar
    try:
        cart_count = len(cart.get_items(st.session_state.cart_id))
    except Exception as e:
        logger.error(f"Failed to get cart count: {e}")
        cart_count = 0
    
    # Render navigation
    render_navbar(cart_count)
    
    # Render current tab
    try:
        if st.session_state.current_tab == "Home":
            render_home()
            
        elif st.session_state.current_tab == "Products":
            render_products(products, cart)
            
        elif st.session_state.current_tab == "Cart":
            render_cart(cart, product_map, products)
            
        elif st.session_state.current_tab == "Checkout":
            render_checkout(cart, product_store, product_map)
            
        elif st.session_state.current_tab == "Order History":
            render_order_history(product_store)
            
    except Exception as e:
        logger.error(f"Error rendering {st.session_state.current_tab} tab: {e}")
        st.error("An error occurred while loading this page")

if __name__ == "__main__":
    main()