const express = require('express');
const mysql = require('mysql2/promise');
const multer = require('multer');
const cors = require('cors');
const base64 = require('base64-js');

const app = express();
app.use(cors());
app.use(express.json());

// Database configuration
const dbConfig = {
  host: 'sql12.freesqldatabase.com',
  user: 'sql12759567',
  password: 'hs9gUGyBB9',
  database: 'sql12759567'
};

// Create a connection pool
const pool = mysql.createPool(dbConfig);

// Set up Multer for handling multipart/form-data requests
const upload = multer({
  dest: './uploads/',
  limits: { fieldSize: 1024 * 1024 * 5 } // 5MB
});

// API endpoint to add a new product
app.post('/add_product', upload.fields([{ name: 'image_1', maxCount: 1 }, { name: 'image_2', maxCount: 1 }, { name: 'image_3', maxCount: 1 }]), async (req, res) => {
  try {
    const { name, category, subcategories, price, stock, description } = req.body;
    const images = [req.files.image_1, req.files.image_2, req.files.image_3];

    // Convert images to binary data
    const imageBinaries = images.map((image) => {
      if (image) {
        return image[0].buffer;
      } else {
        return null;
      }
    });

    // Insert into the database
    const [result] = await pool.execute(`
      INSERT INTO products (name, category, subcategories, price, stock, description, image_1, image_2, image_3)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [name, category, JSON.stringify(subcategories), price, stock === 'Yes', description, imageBinaries[0], imageBinaries[1], imageBinaries[2]]);

    res.json({ message: 'Product added successfully!' });
  } catch (error) {
    console.error('Error while adding product:', error);
    res.status(500).json({ error: 'Failed to add product' });
  }
});

// API endpoint to fetch all products
app.get('/products', async (req, res) => {
  try {
    const [products] = await pool.execute('SELECT * FROM products');

    // Process images and subcategories
    products.forEach((product) => {
      product.subcategories = JSON.parse(product.subcategories);
      for (let i = 1; i <= 3; i++) {
        const imageKey = `image_${i}`;
        if (product[imageKey]) {
          product[imageKey] = `data:image/jpeg;base64,${base64.fromByteArray(product[imageKey])}`;
        } else {
          product[imageKey] = null;
        }
      }
    });

    res.json({ products });
  } catch (error) {
    console.error('Error while fetching products:', error);
    res.status(500).json({ error: 'Failed to fetch products' });
  }
});

// Start the server
const port = 3007;
app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
