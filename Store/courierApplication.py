from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import or_, and_
from configuration import Configuration
from models import database, Product, Category, ProductCategory, ProductOrder, Order
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request, JWTManager
import csv
from ethConfiguration import web3, owner, solidityContract, abi, bytecode
from web3 import Account
from web3.exceptions import ContractLogicError
import json

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

@application.route("/orders_to_deliver", methods=["GET"])
@roleCheck(role = "courier")
def orders_to_deliver():
    ordersInSystem = Order.query.filter(Order.status == "CREATED").all()
    orders = []
    for order in ordersInSystem:
        orders.append({
            "id":order.id,
            "email":order.customer
        })

    return jsonify({"orders":orders}),200

@application.route("/pick_up_order", methods=["POST"])
@roleCheck(role = "courier")
def pick_up_order():
    id = request.json.get("id", "")
    emptyId = len(str(id)) == 0
    if(emptyId):
        return jsonify({"message":"Missing order id."}),400
    if(not isinstance(id,int) or id < 1):
        return jsonify({"message": "Invalid order id."}), 400

    order = Order.query.filter(and_((Order.id == id), (Order.status == "CREATED"))).first()
    if(order == None):
        return jsonify({"message": "Invalid order id."}),400

    # blockchain
    data = request.get_json()
    if ("address" not in data or ("address" in data and len(str(data["address"])) == 0)):
        return jsonify({"message": "Missing address."}), 400

    addr = data["address"]

    if (not web3.is_address(addr)):
        return jsonify({"message": "Invalid address."}), 400

    try:
        orderContract = web3.eth.contract(address=order.contract, abi=abi)
        transactionHash = orderContract.functions.pick_up_order(addr).transact({
            "from": owner
        })
        transactionReceipt = web3.eth.wait_for_transaction_receipt(transactionHash)
    except ContractLogicError as error:
        revertError = str(error)
        revertStartIndex = revertError.find("revert ")
        finalError = revertError[revertStartIndex + 7:]
        return jsonify({"message": finalError}), 400

    order.status = "PENDING"
    database.session.commit()

    return Response(status = 200)

@application.route("/", methods=["GET"])
def index():
    return "Hello world!"

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)