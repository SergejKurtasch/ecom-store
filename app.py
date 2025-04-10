import streamlit as st

# App setup
st.set_page_config(page_title="eCommerce Store", layout="wide")

# Dummy product catalog
products = [
    {"id": 1, "name": "Product 1", "price": 20},
    {"id": 2, "name": "Product 2", "price": 30},
    {"id": 3, "name": "Product 3", "price": 25},
]

# Simulated session state cart
if "cart" not in st.session_state:
    st.session_state.cart = []

# Header
st.title("🛍️ Minimalistic eCommerce Store")

# Navigation
tab = st.radio("Navigation", ["Home", "Products", "Recommendations", "Cart", "Checkout"])

# Pages
if tab == "Home":
    st.subheader("Welcome to our store!")
    st.write("Explore products, add them to your cart, and get personalized recommendations.")

elif tab == "Products":
    st.subheader("📦 Browse Products")
    for product in products:
        st.write(f"**{product['name']}** - ${product['price']}")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://via.placeholder.com/150", width=100)
        with col2:
            if st.button(f"Add to Cart {product['id']}"):
                st.session_state.cart.append(product)
                st.success(f"{product['name']} added to cart.")

elif tab == "Recommendations":
    st.subheader("🧠 Recommended for You")
    st.info("Here we’ll show similar items from Neo4j + Redis.")

elif tab == "Cart":
    st.subheader("🛒 Your Shopping Cart")

    if not st.session_state.cart:
        st.warning("Your cart is empty.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.cart):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(item['name'])
            with col2:
                st.write(f"${item['price']}")
            with col3:
                if st.button(f"Remove {i}"):
                    st.session_state.cart.pop(i)
                    st.experimental_rerun()
            total += item['price']
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
