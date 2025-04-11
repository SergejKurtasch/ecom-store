import streamlit as st
from typing import Dict, Any
from models.cart import Cart

from neo4j import GraphDatabase

# Neo4j Connection - Replace with your credentials
NEO4J_URI = "neo4j+s://5e56b2da.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "h-jFkG_yO2J_fyusi1QPy6l80eSD_o-dD6tLqC20ePM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def render_cart(cart: Cart, product_map: Dict[str, Any], products):
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

    st.subheader("Recommendations for You")
    st.write("Based on your cart items, we recommend the following products:")
    # Get recommendations based on the first item in the cart
    cart_items = cart_details.keys()
    recommendations = get_product_recommendations(driver, list(cart_items)[0], st.session_state.cart_id)

    for product in products:
        if product["Product Name"] in recommendations:
            col1, col2 = st.columns([1, 3])
            with col1:
                if product.get('Image'):
                    st.image(product['Image'], width=150)
            
            with col2:
                st.write(f"**{product['Product Name']}**")
                st.write(f"Price: ${product['Price']}")
                if product.get('Description'):
                    st.write(product['Description'])
                

# Function to get product recommendations
# based on items in the cart (only the first item)

def get_product_recommendations(driver, product_name: str, user_origin: str) -> dict:
    """
    Returns recommendations in format:
    {
        'type': 'collaborative'|'category'|'none',
        'message': str,
        'items': list[str]  # max 3 recommendations
    }
    """
    # 1. Collaborative filtering query
    collaborative_query = """
    MATCH (p:Product {name: $product_name})<-[:PURCHASED]-(u:User)-[:PURCHASED]->(others:Product)
    WHERE p <> others
    AND NOT (u:User {name: $user_origin})-[:PURCHASED]->(others)
    WITH others, COUNT(DISTINCT u) AS user_count
    ORDER BY user_count DESC
    RETURN others.name AS recommendation
    LIMIT 3
    """
    
    # 2. Category fallback query
    category_query = """
    MATCH (u:User {name: $user_origin})-[:PURCHASED]->(p:Product {name: $product_name})
    WITH COLLECT(DISTINCT p.category) AS target_categories
    MATCH (rec:Product)
    WHERE rec.category IN target_categories
    AND rec.name <> $product_name
    WITH rec, rec.category AS category, COUNT{(:User)-[:PURCHASED]->(rec)} AS times_purchased
    ORDER BY times_purchased DESC
    RETURN rec.name AS recommendation, category
    LIMIT 3
    """
    
    # Try collaborative filtering first
    with driver.session() as session:
        result = session.run(collaborative_query,
                            {"product_name": product_name, "user_origin": user_origin})
        collaborative_recs = [record["recommendation"] for record in result]
    
    if collaborative_recs:
        return collaborative_recs

    # Fallback to category-based
    with driver.session() as session:
        result = session.run(category_query,
                            {"product_name": product_name, "user_origin": user_origin})
        records = list(result)
        category_recs = [record["recommendation"] for record in records]
        
        if records:
            category = records[0]["category"]
            return category_recs
    
    return []