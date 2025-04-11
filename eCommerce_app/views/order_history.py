import streamlit as st
from models.product_store import ProductStore

def render_order_history(product_store: ProductStore):
    st.subheader("📝 Your Order History")
    
    user_email = st.session_state.get('user_email')
    if not user_email:
        st.warning("Please complete a checkout first to view your order history")
        return
    
    orders = list(product_store.orders.find({"customer.email": user_email}, {"_id": 0}).sort("created_at", -1))
    
    if not orders:
        st.warning("You haven't placed any orders yet.")
    else:
        for order in orders:
            with st.expander(f"Order #{order['cart_id'][:8]} - {order.get('status', 'Pending')} - {order['created_at'].strftime('%Y-%m-%d')}"):
                st.write(f"**Date:** {order['created_at'].strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Status:** {order.get('status', 'Pending')}")
                st.write(f"**Payment Method:** {order.get('payment_method', 'N/A')}")
                
                st.write("**Items:**")
                items_total = 0.0  # Calculate items total for verification
                for item in order['items']:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if item.get('image_url'):
                            st.image(item['image_url'], width=80)
                    with col2:
                        st.write(f"- {item['product_name']}")
                        st.write(f"  Quantity: {item['quantity']} × ${float(item['unit_price']):.2f} = ${float(item['total_price']):.2f}")
                        items_total += float(item['total_price'])
                        if item.get('category'):
                            st.write(f"  Category: {item['category']}")
                
                # Display both stored total and calculated total for verification
                st.write(f"**Calculated Total:** ${items_total:.2f}")
                st.write(f"**Order Total:** ${float(order.get('order_total', 0)):.2f}")