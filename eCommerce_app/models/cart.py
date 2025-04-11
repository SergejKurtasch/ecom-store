import redis
import logging
from typing import Dict, Any, Tuple
from config import REDIS_CONFIG

logger = logging.getLogger(__name__)

class Cart:
    def __init__(self, namespace: str = "cart"):
        try:
            self.r = redis.StrictRedis(**REDIS_CONFIG)
            self.r.ping()
            self.ns = namespace
            logger.info("Redis connected")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    def _key(self, cart_id: str) -> str:
        return f"{self.ns}:{cart_id}"

    def add_item(self, cart_id: str, product_name: str, qty: int = 1):
        """Add item to cart with quantity validation"""
        if qty <= 0:
            raise ValueError("Quantity must be positive")
            
        try:
            key = self._key(cart_id)

            # Check if the cart exists to set TTL only during creation
            if not self.r.exists(key):
                self.r.expire(key, 259200)  # Set TTL for 3 days
                
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