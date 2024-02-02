from pyspark.sql import SparkSession
import json
import os

builder = SparkSession.builder.appName("Calculating product statistics with spark.")

spark = builder.getOrCreate()

databaseUrl = os.environ["DATABASE_URL"]

productOrderDF = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{databaseUrl}:3306/store") \
    .option("dbtable", "store.productorder") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

productDF = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{databaseUrl}:3306/store") \
    .option("dbtable", "store.products") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

orderDF = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{databaseUrl}:3306/store") \
    .option("dbtable", "store.orders") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

joinedDF = productOrderDF \
        .join(orderDF, productOrderDF["orderId"] == orderDF["id"]) \
        .join(productDF, productOrderDF["productId"] == productDF["id"])

rows = joinedDF.collect()

productDict = {}
for row in rows:
    name = row["name"]
    quantity = row["quantity"]
    if name not in productDict.keys():
        productDict[name] = {"name":name, "sold":0, "waiting":0}
    if(row["status"] == "COMPLETE"):
        productDict[name]["sold"] += quantity
    else:
        productDict[name]["waiting"] += quantity

sortedProductDict = dict(sorted(productDict.items(), key = lambda item: item[0]))
productList = []
for key, value in sortedProductDict.items():
    productList.append(value)

with open("/app/Store/spark/product_statistics.txt", "w") as psfile:
    psfile.write(json.dumps({"statistics":productList}))

# Stop the Spark session
spark.stop()