import streamlit as st

st.set_page_config(page_title="Minimal eCommerce Store", layout="wide")

st.title("🛍️ Minimalistic eCommerce Store")

# Sidebar
st.sidebar.header("Shopping Cart")
st.sidebar.text("🛒 Cart items will appear here")
# In final version: populate from Redis

# Tabs or Sections
tab = st.radio("Choose a section", ["Home", "Products", "Recommendations", "Checkout"])

if tab == "Home":
    st.subheader("Welcome to the Store!")
    st.write("This is a demo of how our e-commerce app will work using Streamlit.")

elif tab == "Products":
    st.subheader("📦 Product Catalog")
    st.info("Here we’ll load data from MongoDB.")
    # Placeholder UI
    for i in range(3):
        st.image("https://via.placeholder.com/150", width=100)
        st.write(f"Product {i + 1}")
        st.button(f"Add to Cart {i + 1}")

elif tab == "Recommendations":
    st.subheader("🧠 Similar Products")
    st.info("This will be powered by Neo4j + Redis (cached).")
    st.write("When you click a product, similar items will show here.")

elif tab == "Checkout":
    st.subheader("💳 Checkout")
    st.info("Final cart data will be sent to MongoDB.")
    st.button("Confirm Purchase")