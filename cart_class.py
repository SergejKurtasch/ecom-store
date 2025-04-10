import redis 

class Cart:
    # Initializes the Cart object with a Redis connection and a namespace for keys.
    def __init__(
        self,
        host: str = "redis-15042.c328.europe-west3-1.gce.redns.redis-cloud.com",
        port=15042, 
        username='Admin', 
        password='Ir0nh@ck', 
        namespace: str = "cart"
    ):
        self.r = redis.StrictRedis(host=host, port=port, username=username, password=password, db=0, decode_responses=True)
        self.ns = namespace

    # Helper method to generate a namespaced Redis key for the given cart ID.
    def _key(self, cart_id: str) -> str:
        return f"{self.ns}:{cart_id}"

    # Adds a product to the cart or updates the quantity if it already exists.
    def add_item(self, cart_id: str, product_name: str, price: float, qty: int = 1):
        key = self._key(cart_id)
        
        # Check if the product already exists in the cart
        quantity_key = f"{product_name}:quantity"
        price_key = f"{product_name}:price"
        
        current_quantity = int(self.r.hget(key, quantity_key) or 0)
        new_quantity = current_quantity + qty

        # Update quantity and price
        self.r.hset(key, price_key, price)
        self.r.hset(key, quantity_key, new_quantity)

    # Removes or decreases the quantity of a product in the cart.
    # If the quantity reaches 0, the product is removed from the cart entirely.
    def remove_item(self, cart_id, product_name, quantity):
        key = self._key(cart_id)

        quantity_key = f"{product_name}:quantity"
        price_key = f"{product_name}:price"

        # Retrieve the current quantity and price of the product
        current_quantity = int(self.r.hget(key, quantity_key) or 0)
        current_price = self.r.hget(key, price_key)

        # Decrease the quantity
        new_quantity = current_quantity - quantity

        if new_quantity <= 0:
            # If quantity is zero or less, remove the product from the cart
            self.r.hdel(key, quantity_key)
            self.r.hdel(key, price_key)
        else:
            # Update the quantity without changing the price
            self.r.hset(key, quantity_key, new_quantity)

    # Retrieves all items in a specific cart.
    def get_cart_items(self, cart_id: str):
        key = self._key(cart_id)
        return self.r.hgetall(key)

    # Deletes an entire cart, removing all items within it.
    def remove_cart(self, cart_id: str):
        self.r.delete(self._key(cart_id))

    # Retrieves and prints all carts along with their data, categorized by Redis data type.
    def get_all_carts(self):
        cursor = 0
        while True:
            cursor, keys = self.r.scan(cursor=cursor, match=f"{self.ns}:*", count=100)
            for key in keys:
                key_type = self.r.type(key)
                if key_type == 'string':
                    value = self.r.get(key)
                elif key_type == 'hash':
                    value = self.r.hgetall(key)
                elif key_type == 'list':
                    value = self.r.lrange(key, 0, -1)
                elif key_type == 'set':
                    value = self.r.smembers(key)
                elif key_type == 'zset':
                    value = self.r.zrange(key, 0, -1, withscores=True)
                else:
                    value = '(Unknown type)'
                print(f'{key} ({key_type}): {value}')
            if cursor == 0:
                break

    # Retrieves all items in a cart, calculates the total for each product,
    # and computes the total sum of all items in the cart.
    def get_sum_items(self, cart_id: str):
        key = self._key(cart_id)
        cart_data = self.r.hgetall(key)  # Retrieve all cart data
        items = []
        total_sum = 0

        for field, value in cart_data.items():
            # Split product name and attribute
            product_name, attribute = field.split(":")
            
            # Check if the current product is already in the list
            existing_item = next((item for item in items if item["name"] == product_name), None)
            
            if not existing_item:
                # If the product is not yet added, create its structure
                existing_item = {"name": product_name, "price": 0, "quantity": 0, "total": 0}
                items.append(existing_item)
            
            # Fill in the product data
            if attribute == "price":
                existing_item["price"] = float(value)
            elif attribute == "quantity":
                existing_item["quantity"] = int(value)
                existing_item["total"] = existing_item["price"] * existing_item["quantity"]

        # Calculate the total sum
        total_sum = sum(item["total"] for item in items)

        # Return the list of products and the total sum
        return items, total_sum
