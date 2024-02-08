from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import or_, and_
from configuration import Configuration
from models import database, Product, Category, ProductCategory, ProductOrder, Order
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request, JWTManager
import csv
from datetime import datetime
from ethConfiguration import web3, owner, solidityContract, abi, bytecode
from web3 import Account
from web3.exceptions import ContractLogicError
import json
import math

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

@application.route("/search", methods=["GET"])
@roleCheck(role = "customer")
def search():
    productName = request.args.getlist('name', None)
    categoryName = request.args.getlist('category', None)

    query = (
        database.session.query(Product, ProductCategory, Category)
        .join(ProductCategory, ProductCategory.productId == Product.id)
        .join(Category, ProductCategory.categoryId == Category.id)
    )

    filterListFirst = []
    if(productName):
        filterListFirst = [Product.name.ilike(f"%{elem}%") for elem in productName]
    filterListSecond = []
    if (categoryName):
        filterListSecond = [Category.id.ilike(f"%{elem}%") for elem in categoryName]

    ff = None
    if filterListFirst:
        ff = or_(*filterListFirst)
    fs = None
    if filterListSecond:
        fs = or_(*filterListSecond)

    productCategories = None

    if(productName and categoryName):
        productCategories = query.filter(and_(ff, fs)).all()
    elif (productName):
        productCategories = query.filter(ff).all()
    elif (categoryName):
        productCategories = query.filter(fs).all()
    else:
        productCategories = query.all()

    categories = []
    ids = set()

    for product, productCategory, category in productCategories:
        if category.id not in categories:
            categories.append(productCategory.categoryId)

    productList = []

    for product, productCategory, category in productCategories:
        if product.id not in ids:
            productList.append(
                {
                    "categories": [category.id for category in product.categories],
                    "id": product.id,
                    "name": product.name,
                    "price": product.price
                }
            )
            ids.add(product.id)

    responseData = {
        "categories": categories,
        "products": productList
    }
    return jsonify(responseData), 200

@application.route("/order", methods=["POST"])
@roleCheck("customer")
def order():
    data = request.get_json()

    if("requests" not in data):
        return jsonify({"message":"Field requests is missing."}), 400

    requestList = data["requests"]
    reqProductsId = []
    reqProductQuantities = []
    # validation
    for i in range(len(requestList)):
        req = requestList[i]
        if("id" not in req):
            return jsonify({"message":f"Product id is missing for request number {i}."}), 400

        if("quantity" not in req):
            return jsonify({"message":f"Product quantity is missing for request number {i}."}), 400

        if(not isinstance(req["id"], int) or req["id"] < 1):
            return jsonify({"message":f"Invalid product id for request number {i}."}), 400

        if(not isinstance(req["quantity"], int) or req["quantity"] < 0):
            return jsonify({"message":f"Invalid product quantity for request number {i}."}), 400

        reqProductsId.append(req["id"])
        reqProductQuantities.append(req["quantity"])

    existingProducts = Product.query.filter(Product.id.in_(reqProductsId)).all()
    if(len(existingProducts) != len(reqProductsId)):
        pids = []
        for product in existingProducts:
            pids.append(product.id)
        for i in range(len(reqProductsId)):
            if(reqProductsId[i] not in pids):
                return jsonify({"message": f"Invalid product for request number {i}."}), 400

    dictExistingProducts = {}
    for product in existingProducts:
        dictExistingProducts[product.id] = product

    if("address" not in data or ("address" in data and len(str(data["address"])) == 0)):
        return jsonify({"message":"Field address is missing."}), 400

    addr = data["address"]

    if(not web3.is_address(addr)):
        return jsonify({"message":"Invalid address."}), 400

    # validations passed
    price = 0
    for i in range(len(reqProductsId)):
        price += dictExistingProducts[reqProductsId[i]].price * reqProductQuantities[i]

    transactionHash = solidityContract.constructor(addr, math.ceil(price)).transact({
        "from": owner
    })
    transactionReceipt = web3.eth.wait_for_transaction_receipt(transactionHash)
    contractAddress = transactionReceipt.contractAddress

    o = Order(totalPrice = price, status = "CREATED", datetime = datetime.now(), customer = get_jwt_identity(), contract = contractAddress)
    database.session.add(o)
    database.session.commit()

    for i in range(len(reqProductsId)):
        product = reqProductsId[i]
        po = ProductOrder(productId = product, orderId = o.id, quantity=reqProductQuantities[i])
        database.session.add(po)
    database.session.commit()

    return jsonify({"id":o.id}), 200

@application.route("/status", methods=["GET"])
@roleCheck("customer")
def status():
    email = get_jwt_identity()
    query = (
        database.session.query(ProductOrder, Order, Product)
        .join(Order, ProductOrder.orderId == Order.id)
        .join(Product, ProductOrder.productId == Product.id)
        .filter(Order.customer == email)
    )

    orderedProducts = query.all()
    products = []
    prevOrderId = None
    oldCreated = False
    o = None
    orders = []
    lastOrder = None
    for productOrder, order, product in orderedProducts:
        lastOrder = {
            "products": [],
            "price": order.totalPrice,
            "status": order.status,
            "timestamp": order.datetime
        }
        if(not oldCreated):
            o = {
                "products": [],
                "price":order.totalPrice,
                "status":order.status,
                "timestamp":order.datetime
            }
            oldCreated = True
        if(prevOrderId != order.id and prevOrderId != None):
            o["products"] = products.copy()
            products.clear()
            orders.append(o.copy())
            oldCreated = False
            o = None
        p = {
                "categories": [cat.id for cat in product.categories],
                "name":product.name,
                "price":product.price,
                "quantity":productOrder.quantity
        }
        products.append(p)
        prevOrderId = order.id
    if(lastOrder != None):
        if(o == None):
            lastOrder["products"] = products.copy()
            orders.append(lastOrder)
        else:
            o["products"] = products.copy()
            orders.append(o.copy())
    return jsonify({"orders":orders}), 200

@application.route("/delivered", methods=["POST"])
@roleCheck("customer")
def delivered():
    id = request.json.get("id", "")
    emptyId = len(str(id)) == 0
    if(emptyId):
        return jsonify({"message":"Missing order id."}),400
    if(not isinstance(id,int) or id < 1):
        return jsonify({"message": "Invalid order id."}), 400

    order = Order.query.filter(and_((Order.id == id), (Order.status == "PENDING"))).first()
    if(order == None):
        return jsonify({"message": "Invalid order id."}),400

    # blockchain
    keys = request.json.get("keys", "")
    emptyKeys = len(str(keys)) == 0
    if(emptyKeys):
        return jsonify({"message": "Missing keys."}),400

    passphrase = request.json.get("passphrase", "")
    emptyPassphrase = len(str(passphrase)) == 0
    if(emptyPassphrase):
        return jsonify({"message": "Missing passphrase."}), 400

    keys = json.loads(keys.replace("'",'"'))

    try:
        address = web3.to_checksum_address(keys["address"])
        privateKey = Account.decrypt(keys, passphrase).hex()
        try:
            orderContract = web3.eth.contract(address = order.contract, abi = abi)
            transaction = orderContract.functions.delivery().build_transaction({
                "from": address,
                "nonce": web3.eth.get_transaction_count(address),
                "gasPrice": 21000
            })
            signedTransaction = web3.eth.account.sign_transaction(transaction, privateKey)
            transactionHash = web3.eth.send_raw_transaction(signedTransaction.rawTransaction)
            transactionReceipt = web3.eth.wait_for_transaction_receipt(transactionHash)
        except ContractLogicError as error:
            revertError = str(error)
            revertStartIndex = revertError.find("revert ")
            finalError = revertError[revertStartIndex + 7:]
            return jsonify({"message": finalError}), 400

    except ValueError:
        return jsonify({"message": "Invalid credentials."}), 400

    # regular
    order.status = "COMPLETE"
    database.session.commit()

    return Response(status = 200)

@application.route("/pay", methods=["POST"])
@roleCheck("customer")
def pay():
    id = request.json.get("id", "")
    emptyId = len(str(id)) == 0
    if (emptyId):
        return jsonify({"message": "Missing order id."}), 400

    if(not isinstance(id,int) or id < 1):
        return jsonify({"message": "Invalid order id."}), 400

    order = Order.query.filter(Order.id == id).first()
    if(order == None):
        return jsonify({"message": "Invalid order id."}),400

    data = request.get_json()

    if("keys" not in data or ("keys" in data and data["keys"] == "")):
        return jsonify({"message":"Missing keys."}), 400

    if("passphrase" not in data or ("passphrase" in data and data["passphrase"] == "")):
        return jsonify({"message":"Missing passphrase."}), 400

    keys = request.json.get("keys", "")
    # emptyKeys = len(str(keys))
    # if(emptyKeys):
    #     return jsonify({"message": "Missing keys."}), 400

    passphrase = request.json.get("passphrase", "")
    # emptyPassphrase = len(str(passphrase)) == 0
    # if (emptyPassphrase):
    #     return jsonify({"message": "Missing passphrase."}), 400

    keys = json.loads(keys.replace("'", '"'))

    try:
        address = web3.to_checksum_address(keys["address"])
        privateKey = Account.decrypt(keys, passphrase).hex()
        try:
            orderContract = web3.eth.contract(address = order.contract, abi = abi)
            transaction = orderContract.functions.pay().build_transaction({
                "from": address,
                "value": math.ceil(order.totalPrice),
                "nonce": web3.eth.get_transaction_count(address),
                "gasPrice": 21000
            })
            signedTransaction = web3.eth.account.sign_transaction(transaction, privateKey)
            transactionHash = web3.eth.send_raw_transaction(signedTransaction.rawTransaction)
            transactionReceipt = web3.eth.wait_for_transaction_receipt(transactionHash)
        except ContractLogicError as error:
            revertError = str(error)
            revertStartIndex = revertError.find("revert ")
            finalError = revertError[revertStartIndex + 7:]
            return jsonify({"message": finalError}), 400

    except ValueError:
        return jsonify({"message": "Invalid credentials."}), 400

    return jsonify(), 200


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)