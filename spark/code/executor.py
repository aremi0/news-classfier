print("_______________executor________________")

from pyspark.sql import SparkSession
from elasticsearch import Elasticsearch
from os.path import exists
import pyspark.sql.types as types
from pyspark.sql.functions import from_json, to_date, col, array, to_timestamp
from pyspark.ml import PipelineModel


trainingPath = "/opt/tap/training"
APP_NAME = 'news-classfier'

elastic_host="http://elasticsearch:9200"
elastic_index="news_index"

kafkaServer="kafkaServer:9092"
topic = "articles"

# Define elasticsearch schema to be sended
elastic_mapping = {
    "mappings": {
        "properties": 
            {
                "title": {"type": "text"},
                "description": {"type": "text"},
                "publish_date": {"type": "date", "format": "yyyyMMddHHmmss"},
                "predictedString": {"type": "text", "fielddata": True},
                "source_url": {"type": "text"},
                "country_name": {"type": "text"},
                "country_code": {"type": "keyword"},
                "location": {"type": "geo_point"},
                "host": {"type": "text", "fielddata": True}
            }
    }
}

# Define articles schema structure to be readed from kafka
articlesSchema = types.StructType([
    types.StructField(name='_c0', dataType=types.StringType()),
    types.StructField(name='country_name', dataType=types.StringType()),
    types.StructField(name='country_code', dataType=types.StringType()),
    types.StructField(name='latitude', dataType=types.StringType()),
    types.StructField(name='longitude', dataType=types.StringType()),
    types.StructField(name='source_url', dataType=types.StringType()),
    types.StructField(name='title', dataType=types.StringType()),
    types.StructField(name='description', dataType=types.StringType()),
    types.StructField(name='text', dataType=types.StringType()),
    types.StructField(name='publish_date', dataType=types.StringType()),
])


# create elasticsearch session and index
es = Elasticsearch(elastic_host, verify_certs=False)
print("______________________________________________")
es.indices.create(index=elastic_index, body=elastic_mapping, ignore=400)


def main() :
    if not exists(trainingPath):
        print("There's no trained model here! You have to execute Trainer first!")
        exit()


    # create a new spark session
    spark = SparkSession.builder.master("local[*]")\
                                .appName(APP_NAME)\
                                .config("spark.es.nodes", elastic_host)\
                                .config("spark.es.nodes.wan.only", "true")\
                                .config("spark.es.net.ssl", "true")\
                                .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR") # Reduce the verbosity of logging messages

    print("Loading trained model...")
    model = PipelineModel.load(trainingPath)

    # Timestamp will be extracted from kafka
    print("Reading stream from kafka...")
    df = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", kafkaServer) \
        .option("startingOffsets", "earliest") \
        .option("subscribe", topic) \
        .load() \
        .selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value").cast("string"), articlesSchema).alias("data")) \
        .selectExpr("data.*") \
        .na.drop() # There is only one row that container all headers to None that cause crash

    # Apply the machine learning model and select only the interesting casted columns
    print("Applying ml model to data before transfer...")
    df = model.transform(df) \
        .withColumn("latitude", df.latitude.cast(types.DoubleType())) \
        .withColumn("longitude", df.longitude.cast(types.DoubleType())) \
        .withColumn("location", array(col('longitude'), col('latitude')))

    result = df.select("title", "description", "publish_date", "predictedString", \
                        "source_url","country_name", "country_code", "location") \
                .selectExpr("*", "parse_url(source_url, 'HOST') AS host")
    
    print("Moving data to elasticsearch...")
    query = result.writeStream \
        .outputMode("append") \
        .format("org.elasticsearch.spark.sql") \
        .option("checkpointLocation", "/tmp/") \
        .option("es.resource", elastic_index) \
        .option("es.nodes", elastic_host) \
        .start()
    
    query.awaitTermination()


if __name__ == "__main__":
    main()

