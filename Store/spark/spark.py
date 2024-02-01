from flask import Flask
import os
import subprocess

application = Flask(__name__)

@application.route("/category_statistics", methods=["GET"])
def category_statistics():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/Store/spark/category_statistics.py"
    os.environ["SPARK_SUBMIT_ARGS"] = \
        "--driver-class-path /app/Store/spark/mysql-connector-j-8.0.33.jar" \
        " --jars /app/Store/spark/mysql-connector-j-8.0.33.jar"
    subprocess.run(["/template.sh"])
    with open("/app/Store/spark/category_statistics.txt", "r") as csfile:
        cs = csfile.read()
    return cs

@application.route("/product_statistics", methods=["GET"])
def product_statistics():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/Store/spark/product_statistics.py"
    os.environ["SPARK_SUBMIT_ARGS"] = \
        "--driver-class-path /app/Store/spark/mysql-connector-j-8.0.33.jar" \
        " --jars /app/Store/spark/mysql-connector-j-8.0.33.jar"
    subprocess.run(["/template.sh"])
    with open("/app/Store/spark/product_statistics.txt", "r") as psfile:
        ps = psfile.read()
    return ps

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5004)