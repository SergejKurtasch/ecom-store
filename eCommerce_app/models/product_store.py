from pymongo import MongoClient
from datetime import datetime
import logging
from typing import Dict, Any, List, Tuple
from config import MONGO_URL, DB_NAME

logger = logging.getLogger(__name__)

class ProductStore:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URL)
            self.db = self.client[DB_NAME]
            self.products = self.db["Products"]
            self.orders = self.db["Orders"]
            logger.info("MongoDB connected")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
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