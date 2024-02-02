from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum
import json
import os

builder = SparkSession.builder.appName("Calculating category statistics with spark.")

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

productCategoryDF = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{databaseUrl}:3306/store") \
    .option("dbtable", "store.productcategory") \
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

categoryDF = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{databaseUrl}:3306/store") \
    .option("dbtable", "store.categories") \
    .option("user", "root") \
    .option("password", "root") \
    .load()


# Join ProductOrder with Order, Product, and ProductCategory
joinedDF = productOrderDF \
    .join(orderDF, productOrderDF["orderId"] == orderDF["id"]) \
    .join(productDF, productOrderDF["productId"] == productDF["id"]) \
    .join(productCategoryDF, productDF["id"] == productCategoryDF["productId"]) \
    .join(categoryDF.alias("cat_alias"), productCategoryDF["categoryId"] == col("cat_alias.id")) \
    .filter(orderDF["status"] == "COMPLETE")

# Explicitly cast the 'quantity' column to a numeric type
joinedDF = joinedDF.withColumn("quantity", col("quantity").cast("double"))

# Aggregate by category and sum the quantities
categoryQuantities = joinedDF.groupBy("cat_alias.id").agg(sum("quantity").alias("total_quantity"))

# Collect the data into a list of rows
categoryRows = categoryQuantities.collect()

categoryDict = {}

# Initialize categoryDict
for cat in categoryDF.collect():
    categoryDict[cat["id"]] = 0

# Iterate over the collected rows and populate the dictionary
for row in categoryRows:
    categoryDict[row["id"]] = row["total_quantity"]

# Sorting the dictionary by quantity (descending) and then by category id (ascending)
sortedCategories = dict(sorted(categoryDict.items(), key=lambda item: (-item[1], item[0])))

categoryList = list(sortedCategories.keys())

# Writing the result to a JSON file
with open("/app/Store/spark/category_statistics.txt", "w") as csfile:
    csfile.write(json.dumps({"statistics": categoryList}))

# Stop the Spark session
spark.stop()