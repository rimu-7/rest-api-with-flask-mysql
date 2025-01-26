from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import base64
import json
import os

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    "host": "sql12.freesqldatabase.com",
    "user": "sql12759567",
    "password": "hs9gUGyBB9",
    "database": "sql12759567"
}


@app.route("/")
def get_home():
    return "hello world"


def get_db_connection():
    """Establish a new database connection."""
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/add_product/", methods=["POST"])
def add_product():
    """API endpoint to add a new product."""
    try:
        data = request.form
        images = request.files
        name = data.get("name")
        category = data.get("category")
        subcategories = data.getlist("subcategories[]")
        price = float(data.get("price", 0))
        stock = data.get("stock") == "Yes"
        description = data.get("description")

        # Read image binary data
        image_binaries = []
        for i in range(3):
            image_key = f"image_{i + 1}"
            if image_key in images:
                file = images[image_key]
                image_binaries.append(file.read())  # Convert image to binary
            else:
                image_binaries.append(None)

        # Insert into the database
        db = get_db_connection()
        cursor = db.cursor()
        sql = """
        INSERT INTO products (name, category, subcategories, price, stock, description, image_1, image_2, image_3)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql,
            (
                name,
                category,
                json.dumps(subcategories),
                price,
                stock,
                description,
                image_binaries[0],
                image_binaries[1],
                image_binaries[2],
            ),
        )
        db.commit()
        db.close()
        return jsonify({"message": "Product added successfully!"}), 201
    except Exception as e:
        print(f"Error while adding product: {e}")
        return jsonify({"error": "Failed to add product"}), 500


@app.route("/products", methods=["GET"], strict_slashes=False)
def get_products():
    """API endpoint to fetch all products."""
    try:
        db = get_db_connection()
        cursor = db.cursor()
        sql = "SELECT * FROM products"
        cursor.execute(sql)
        products = cursor.fetchall()
        db.close()

        # Process images and subcategories
        for product in products:
            product["subcategories"] = json.loads(product["subcategories"])
            for i in range(1, 4):
                image_key = f"image_{i}"
                if product[image_key]:
                    product[image_key] = f"data:image/jpeg;base64,{base64.b64encode(product[image_key]).decode('utf-8')}"
                else:
                    product[image_key] = None

        return jsonify({"products": products}), 200
    except Exception as e:
        print(f"Error while fetching products: {e}")
        return jsonify({"error": "Failed to fetch products"}), 500


if __name__ == "__main__":
    # Vercel uses PORT from the environment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
