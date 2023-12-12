from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User, UserRole, Role
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import and_
import re

application = Flask(__name__)
application.config.from_object(Configuration)

def is_valid_email(email):
    # Regular expression for a simple email format check
    email_regex = r'^\S+@\S+\.com$'

    # Check if the email matches the regular expression
    if re.match(email_regex, email):
        return True
    else:
        return False

@application.route("/register_courier", methods=["POST"])
def register_courier():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0
    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    errMsg = ""
    exception = False
    if forenameEmpty:
        errMsg += "Field forename is missing."
        return jsonify({"message": errMsg}), 400
    if surnameEmpty:
        errMsg += "Field surname is missing."
        return jsonify({"message": errMsg}), 400
    if emailEmpty:
        errMsg += "Field email is missing."
        return jsonify({"message": errMsg}), 400
    if passwordEmpty:
        errMsg += "Field password is missing."
        return jsonify({"message": errMsg}), 400

    result = parseaddr(email)
    if len(result[1]) == 0 or not is_valid_email(email):
        return jsonify({"message": "Invalid email."}), 400

    if len(password) < 8:
        return jsonify({"message": "Invalid password."}), 400

    user = User.query.filter(User.email == email).first()
    if user:
        return jsonify({"message": "Email already exists."}), 400

    newUser = User(email=email, password=password, forename=forename, surname=surname)
    database.session.add(newUser)
    database.session.commit()

    # role = Role.query.filter(Role.name == "courier").first()
    userRole = UserRole(userId=newUser.id, roleId="courier")
    database.session.add(userRole)
    database.session.commit()

    return Response(status=200)

@application.route("/register_customer", methods=["POST"])
def register_customer():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0
    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    errMsg = ""
    exception = False
    if forenameEmpty:
        errMsg += "Field forename is missing."
        return jsonify({"message": errMsg}), 400
    if surnameEmpty:
        errMsg += "Field surname is missing."
        return jsonify({"message": errMsg}), 400
    if emailEmpty:
        errMsg += "Field email is missing."
        return jsonify({"message": errMsg}), 400
    if passwordEmpty:
        errMsg += "Field password is missing."
        return jsonify({"message": errMsg}), 400

    result = parseaddr(email)
    if len(result[1]) == 0 or not is_valid_email(email):
        return jsonify({"message": "Invalid email."}), 400

    if len(password) < 8:
        return jsonify({"message": "Invalid password."}), 400

    user = User.query.filter(User.email == email).first()
    if user:
        return jsonify({"message": "Email already exists."}), 400

    newUser = User(email=email, password=password, forename=forename, surname=surname)
    database.session.add(newUser)
    database.session.commit()

    # role = Role.query.filter(Role.name == "customer").first()
    userRole = UserRole(userId=newUser.id, roleId="customer")
    database.session.add(userRole)
    database.session.commit()

    return Response(status=200)

jwt = JWTManager(application)

@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    errMsg = ""

    if emailEmpty:
        errMsg += "Field email is missing."
        return jsonify({"message": errMsg}), 400
    if passwordEmpty:
        errMsg += "Field password is missing."
        return jsonify({"message": errMsg}), 400

    result = parseaddr(email)
    if len(result[1]) == 0 or not is_valid_email(email):
        return jsonify({"message": "Invalid email."}), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        return jsonify({"message": "Invalid credentials."}), 400

    roleList = [role.id for role in user.roles]
    roleString = ""
    for i in range(len(roleList)):
        roleString += roleList[i]
        if (i != len(roleList) - 1):
            roleString += " "

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "password": user.password,
        "roleId": roleString
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken), 200

@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    subject = get_jwt_identity()  # get subject
    additionalClaims = get_jwt()  # get payload in the form of a dictionary

    user = User.query.filter(User.email == subject).first()
    if not user:
        return jsonify({"message": "Unknown user."}), 400

    userRoles = UserRole.query.filter(UserRole.userId == user.id)

    for userRole in userRoles:
        database.session.delete(userRole)
    database.session.delete(user)
    database.session.commit()

    return Response(status=200)

# function which checks when an image has been created
@application.route("/", methods=["GET"])
def index():
    return "Hello world!"

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5000)
