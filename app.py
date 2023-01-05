from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from waitress import serve
from Models.Products import Products
from Models.Categories import Categories
from Models.Users import Users
from Models.Carts import Carts

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the random string'    
cors = CORS(app)

def get_database():
  """
    input: none
    output: một database
  """
  uri = "mongodb+srv://demoMongoDB:admin@demo-mongodb.izjqv.mongodb.net/?retryWrites=true&w=majority"
  client = MongoClient(uri, serverSelectionTimeoutMS=5000)
  try:
    return client["DoAn"]
  except Exception:
    print("Unable to connect to the server.")

@app.route("/", methods=["GET"])
def hello():
  return jsonify(msg="Hello")

@app.route("/products", methods=["GET"])
def get_products():
  """
    input: từ query params thông qua phương thức HTTP GET
    output: json object, status_code
  """
  req = request.args.to_dict()
  db = get_database()
  products = Products(db)
  res, status_code = products.get_products(req)
  return jsonify(res), status_code

@app.route('/products/<int:product_id>', methods=["GET"])
def get_product_detail(product_id):
  """
    input: product_id từ pathname thông qua phương thức HTTP GET
    output: json object, status_code
  """

  db = get_database()
  products = Products(db)
  res, status_code = products.get_product_detail(product_id)
  return jsonify(res), status_code

@app.route('/products/count_products_by_categories', methods=["GET"])
def count_products_by_categories():
  """
    input: none
    output: json object, status_code
  """

  db = get_database()
  products = Products(db)
  res, status_code = products.count_products_by_categories()
  return jsonify(res), status_code

@app.route('/categories/<int:category_id>', methods=["GET"])
def get_category_detail(category_id):
  """
    input: category_id từ pathname thông qua phương thức HTTP GET
    output: json object, status_code
  """

  db = get_database()
  categories = Categories(db)
  res, status_code = categories.get_category_detail(category_id)
  return jsonify(res), status_code

@app.route('/login', methods = ['POST'])
def login():
  """
    input: từ request body thông qua phương thức HTTP POST
    output: json object, status_code
  """

  db = get_database()
  req = request.json
  users = Users(db)
  res, status_code = users.login(req)
  return jsonify(res), status_code

@app.route('/sign_up', methods = ['POST'])
def sign_up():
  """
    input: từ request body thông qua phương thức HTTP POST
    output: json object, status_code
  """

  db = get_database()
  req = request.json
  users = Users(db)
  res, status_code = users.sign_up(req)
  return jsonify(res), status_code

@app.route('/cart', methods = ['POST'])
def add_to_cart():
  """
    input: từ request body thông qua phương thức HTTP POST
    output: json object, status_code
  """

  db = get_database()
  req = request.json
  carts = Carts(db)
  res, status_code = carts.add_to_cart(req)
  return jsonify(res), status_code
  
if __name__ == "__main__":
  app.run()