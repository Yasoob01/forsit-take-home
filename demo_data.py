import random
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models
import string

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def generate_sku():
    """Generate a random SKU"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_demo_data():
    db = SessionLocal()
    try:
        # Create categories
        categories = []
        for category_name in ["Electronics", "Clothing", "Home & Kitchen", "Books", "Toys"]:
            category = models.Category(
                name=category_name,
                description=f"Category for {category_name.lower()} products"
            )
            db.add(category)
            db.flush()
            categories.append(category)
        
        # Create products
        products = []
        product_names = {
            "Electronics": ["Smartphone", "Laptop", "Headphones", "Tablet", "Smart Watch"],
            "Clothing": ["T-Shirt", "Jeans", "Dress", "Jacket", "Shoes"],
            "Home & Kitchen": ["Blender", "Coffee Maker", "Toaster", "Microwave", "Vacuum Cleaner"],
            "Books": ["Fiction Novel", "Cookbook", "Biography", "Self-Help", "Technical Manual"],
            "Toys": ["Action Figure", "Board Game", "Puzzle", "Stuffed Animal", "Building Blocks"]
        }
        
        platforms = ["Amazon", "Walmart"]
        
        for category in categories:
            for name in product_names[category.name]:
                for platform in platforms:
                    price = round(random.uniform(10.0, 500.0), 2)
                    product = models.Product(
                        name=f"{name} - {platform}",
                        description=f"This is a {name.lower()} available on {platform}.",
                        price=price,
                        category_id=category.id,
                        sku=generate_sku()
                    )
                    db.add(product)
                    db.flush()  # To get the product ID
                    products.append(product)
                    
                    # Create inventory for each product
                    quantity = random.randint(0, 100)
                    threshold = random.randint(5, 20)
                    inventory = models.Inventory(
                        product_id=product.id,
                        quantity=quantity,
                        low_stock_threshold=threshold,
                        last_restock_date=datetime.now() - timedelta(days=random.randint(0, 30))
                    )
                    db.add(inventory)
        
        db.commit()
        
        # Create sales data for the past year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        current_date = start_date
        
        order_id_counter = 1000
        
        while current_date <= end_date:
            # Generate 5-15 sales per day
            for _ in range(random.randint(5, 15)):
                # Create a sale with 1-3 items
                order_id = f"ORD-{order_id_counter}"
                order_id_counter += 1
                
                platform = random.choice(platforms)
                customer_id = f"CUST-{random.randint(1000, 9999)}"
                
                # Select 1-3 products for this order
                order_products = random.sample(products, random.randint(1, 3))
                
                total_amount = 0
                sale_items = []
                
                for product in order_products:
                    quantity = random.randint(1, 5)
                    unit_price = product.price
                    subtotal = round(unit_price * quantity, 2)
                    total_amount += subtotal
                    
                    sale_item = {
                        "product_id": product.id,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "subtotal": subtotal
                    }
                    sale_items.append(sale_item)
                
                # Create the sale
                sale = models.Sale(
                    order_id=order_id,
                    order_date=current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                    customer_id=customer_id,
                    total_amount=total_amount,
                    platform=platform,
                    status="completed"
                )
                db.add(sale)
                db.flush()
                
                # Add sale items
                for item_data in sale_items:
                    sale_item = models.SaleItem(
                        sale_id=sale.id,
                        product_id=item_data["product_id"],
                        quantity=item_data["quantity"],
                        unit_price=item_data["unit_price"],
                        subtotal=item_data["subtotal"]
                    )
                    db.add(sale_item)
            
            current_date += timedelta(days=1)
        
        db.commit()
        print("Demo data created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating demo data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()