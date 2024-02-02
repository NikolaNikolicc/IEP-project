from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from configuration import Configuration
from models import database, Product, Category, ProductCategory, ProductOrder, Order
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request, JWTManager
from requests import request as rq
import json
import csv

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            verify_jwt_in_request()
            claims = get_jwt()
            if("roleId" in claims.keys() and (role in claims["roleId"])):
                return function(*arguments, **keywordArguments)
            else:
                return jsonify({"msg":"Missing Authorization Header"}),401
        return decorator
    return innerRole

@application.route("/update", methods=["POST"])
@roleCheck(role = "owner")
def update():
    if("file" not in request.files):
        return jsonify({"message": "Field file is missing."}), 400
    file = request.files["file"].stream.read().decode()
    fileEmpty = len(file) == 0
    if(fileEmpty):
        return jsonify({"message":"Field file is missing."}), 400

    products = file.split("\n")

    # validation
    names = []
    productsForCommit = []
    productCategoryDict = dict()
    categories = set()
    for i in range(len(products)):
        product = products[i].split(",")
        if(len(product) != 3):
            return jsonify({"message":f"Incorrect number of values on line {i}."}), 400
        if(product[0] == "" or product[1] == "" or product[2] == ""):
            return jsonify({"message": f"Incorrect number of values on line {i}."}), 400
        try:
            float(product[2])
        except:
            return jsonify({"message": f"Incorrect price on line {i}."}), 400
        if(float(product[2]) <= 0):
            return jsonify({"message":f"Incorrect price on line {i}."}), 400
        names.append(product[1])
        categs = product[0].split("|")
        productCategoryDict[product[1]] = categs
        for c in categs:
            categories.add(c)

    existingProducts = Product.query.filter(Product.name.in_(names)).all()

    if existingProducts:
        return jsonify({"message": f"Product {existingProducts[0].name} already exists."}), 400

    # validation passed
    for i in range(len(products)):
        product = products[i].split(",")
        p = Product(name = product[1], price = float(product[2]))
        database.session.add(p)

    database.session.commit()

    allExistingCategories = Category.query.all()
    allExistingCategoriesId = [category.id for category in allExistingCategories]
    categoriesForCommit = []
    for category in categories:
        if(category not in allExistingCategoriesId):
            categoriesForCommit.append(Category(id = category))

    for cat in categoriesForCommit:
        database.session.add(cat)

    database.session.commit()

    existingProducts = Product.query.filter(Product.name.in_(names)).all()

    productCategoryForCommit = []
    for product in existingProducts:
        vals = productCategoryDict[product.name]
        for val in vals:
            productCategoryForCommit.append(ProductCategory(productId = product.id, categoryId = str(val)))

    for pc in productCategoryForCommit:
        database.session.add(pc)

    database.session.commit()

    return Response(status=200)

@application.route("/product_statistics", methods=["GET"])
@roleCheck(role = "owner")
def product_statistics():

    # query = (
    #     database.session.query(ProductOrder, Order, Product)
    #     .join(Order, ProductOrder.orderId == Order.id)
    #     .join(Product, ProductOrder.productId == Product.id)
    # )
    #
    # orderedProducts = query.all()
    #
    # productDict = {}
    # for productOrder, order, product in orderedProducts:
    #     if product.name not in productDict.keys():
    #         productDict[product.name] = {"name":product.name, "sold":0, "waiting":0}
    #     if(order.status == "COMPLETE"):
    #         productDict[product.name]["sold"] += productOrder.quantity
    #     else:
    #         productDict[product.name]["waiting"] += productOrder.quantity
    #
    # sortedProductDict = dict(sorted(productDict.items(), key = lambda item:[0]))
    # productList = []
    # for key, value in sortedProductDict.items():
    #     productList.append(value)

    # return jsonify({"statistics":productList}),200

    return jsonify(json.loads(rq(method="get",url="http://sparkApp:5004/product_statistics").text)),200

@application.route("/category_statistics", methods=["GET"])
@roleCheck(role = "owner")
def category_statistics():
    # query = (
    #     database.session.query(ProductOrder, Order, Product)
    #     .join(Order, ProductOrder.orderId == Order.id)
    #     .join(Product, ProductOrder.productId == Product.id)
    #     .filter(Order.status == "COMPLETE")
    # )
    #
    # orderedProducts = query.all()
    #
    # categoryDict = {}
    # categories = Category.query.all()
    # for cat in categories:
    #     categoryDict[cat.id] = 0
    #
    # for productOrder, order, product in orderedProducts:
    #     for cat in product.categories:
    #         categoryDict[cat.id] += productOrder.quantity
    #
    # sortedCategories = dict(sorted(categoryDict.items(), key=lambda item: (-item[1], item[0])))
    # categoryList = []
    # for key in sortedCategories.keys():
    #     categoryList.append(key)

    # return jsonify({"statistics":categoryList}),200

    return jsonify(json.loads(rq(method="get", url="http://sparkApp:5004/category_statistics").text)), 200

@application.route("/", methods=["GET"])
def index():
    return "Hello world!"

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)