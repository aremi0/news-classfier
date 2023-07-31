print("_______________executor________________")

from pyspark.sql import SparkSession
from elasticsearch import Elasticsearch
from os.path import exists
import pyspark.sql.types as types
from pyspark.sql.functions import from_json, to_date, col, array
from pyspark.ml import PipelineModel


trainingPath = "/opt/tap/training/17class"
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
                "publish_date": {"type": "date", "format": "yyyy-MM-dd"},
                "predictedString": {"type": "text", "fielddata": True},
                "prediction": {"type": "byte"},
                "country_name": {"type": "text"},
                "country_code": {"type": "keyword"},
                "location": {"type": "geo_point"}
            }
    }
}

# Define articles schema structure to be readed from kafka
articlesSchema = types.StructType([
    types.StructField(name='_c0', dataType=types.StringType()),
    types.StructField(name='publish_date', dataType=types.StringType()),
    types.StructField(name='country_name', dataType=types.StringType()),
    types.StructField(name='country_code', dataType=types.StringType()),
    types.StructField(name='latitude', dataType=types.StringType()),
    types.StructField(name='longitude', dataType=types.StringType()),
    types.StructField(name='source_url', dataType=types.StringType()),
    types.StructField(name='title', dataType=types.StringType()),
    types.StructField(name='description', dataType=types.StringType()),
    types.StructField(name='text', dataType=types.StringType())
])


# create elasticsearch session and index
es = Elasticsearch(elastic_host, verify_certs=False)
es.indices.create(index=elastic_index, body=elastic_mapping, ignore=400)


def process_batch(batch_df, batch_id) :
    if batch_df.count() > 1 :
        print("___batch_id: ", batch_id)
        print("___batch_df__SIZE: ", batch_df.count())
        batch_df.printSchema()
        batch_df.show()

        for idx, row in enumerate(batch_df.collect()) :
            row_dict = row.asDict()
            #print("___row_dict: ", row_dict)
            id = f'{batch_id}-{idx}'
            es.index(index=elastic_index, id=id, document=row_dict)

        print("___data sended to elasticsearch...")


def main() :
    if not exists(trainingPath):
        print("There's no trained model here! You have to execute Trainer first!")
        exit()


    # create a new spark session
    spark = SparkSession.builder.master("local[*]")\
                                .appName(APP_NAME)\
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
        .selectExpr("CAST(timestamp AS STRING)", "CAST(value AS STRING)") \
        .select("timestamp", from_json(col("value").cast("string"), articlesSchema).alias("data")) \
        .selectExpr("timestamp", "data.*") \
        .na.drop() # There is only one row that container all headers to None that cause crash

    # Apply the machine learning model and select only the interesting casted columns
    df = model.transform(df) \
        .withColumn("latitude", df.latitude.cast(types.DoubleType())) \
        .withColumn("longitude", df.longitude.cast(types.DoubleType())) \
        .withColumn("location", array(col('longitude'), col('latitude'))) \
        .withColumn("publish_date", to_date(df.publish_date, "yyyyMMdd"))

    result = df.select("title", "description", "publish_date", "predictedString", \
                        "prediction","country_name", "country_code", "location") \
    .withColumn("prediction", df.prediction.cast(types.IntegerType()))

    result.writeStream\
    .foreachBatch(process_batch) \
    .start() \
    .awaitTermination()


if __name__ == "__main__":
    main()

