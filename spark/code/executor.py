print("_______________executor________________")

from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark import SparkContext
from elasticsearch import Elasticsearch
from os.path import exists
import pyspark.sql.types as types
from pyspark.sql.functions import from_json, concat_ws, to_date, date_format, col, to_json, array
from pyspark.ml import PipelineModel


trainingPath = "/opt/tap/training/17class"
APP_NAME = 'news-classfier'

elastic_host="http://elasticsearch:9200"
elastic_index="news_index"

kafkaServer="kafkaServer:9092"
topic = "articles"

#** timestamp format
# Define elasticsearch schema to be sended
elastic_mapping = {
    "mappings": {
        "properties": 
            {
                "timestamp": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss.SSS"},
                "title": {"type": "text"},
                "publish_date": {"type": "date", "format": "yyyyMMdd"},
                "predictedString": {"type": "text", "fielddata": True},
                "country_code": {"type": "text", "fielddata": True},
                "location": {"type": "geo_point"}
            }
    }
}

# Define articles schema structure to be readed from kafka
articlesSchema = types.StructType([
    types.StructField(name='_c0', dataType=types.StringType()),
    types.StructField(name='event_id', dataType=types.StringType()),
    types.StructField(name='publish_date', dataType=types.StringType()),
    types.StructField(name='country_code', dataType=types.StringType()),
    types.StructField(name='latitude', dataType=types.StringType()),
    types.StructField(name='longitude', dataType=types.StringType()),
    types.StructField(name='source_url', dataType=types.StringType()),
    types.StructField(name='title', dataType=types.StringType()),
    types.StructField(name='text', dataType=types.StringType()),
])




# create elasticsearch session and index
es = Elasticsearch(elastic_host, verify_certs=False)
es.indices.create(index=elastic_index, body=elastic_mapping, ignore=400)



def process_batch(batch_df, batch_id) :
    if batch_df.count() > 1 :
        print("___batch_id: ", batch_id)
        print("___batch_df__SIZE: ", batch_df.count())

        # Casting non-string column to their original type
        #batch_df = batch_df.withColumn("ActionGeo_Lat", batch_df.ActionGeo_Lat.cast(types.FloatType()))
        #batch_df = batch_df.withColumn("ActionGeo_Long", batch_df.ActionGeo_Long.cast(types.FloatType()))
        #print("___batchSchema after casting: ")
        batch_df.printSchema()

        batch_df.show()

        
        for idx, row in enumerate(batch_df.collect()) :
            row_dict = row.asDict()
            #print("___row_dict: ", row_dict)
            id = f'{batch_id}-{idx}'
            resp = es.index(index=elastic_index, id=id, document=row_dict)

        print("___data sended to elasticsearch...")
        batch_df.show()




def process_batch11111111(batch_df, batch_id) :
    if batch_df.count() > 1 :
        print("___batch_id: ", batch_id)
        print("___batch_df__SIZE: ", batch_df.count())

        # Casting non-string column to their original type
        #batch_df = batch_df.withColumn("PUBLISH_DATE", to_date(batch_df.PUBLISH_DATE, "yyyyMMdd"))
        #batch_df = batch_df.withColumn("ActionGeo_Lat", batch_df.ActionGeo_Lat.cast(types.FloatType()))
        #batch_df = batch_df.withColumn("ActionGeo_Long", batch_df.ActionGeo_Long.cast(types.FloatType()))

        for idx, row in enumerate(batch_df.collect()) :
            row_dict = row.asDict()

            id = f'{batch_id}-{idx}'

            print("___row_dict: ", row_dict)
            es.index(index=elastic_index, id=id, document=row_dict)

        print("___data sended to elasticsearch...")
        batch_df.show()




def main() :
    if not exists(trainingPath):
        print("There's no trained model here! You have to execute Trainer first!")
        exit()


    # create a new spark session
    spark = SparkSession.builder.master("local[*]")\
                                .appName(APP_NAME)\
                                .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR") # Reduce the verbosity of logging messages



    # create a new spark session
    #sparkConf = SparkConf().set("es.nodes", "elasticsearch") \
    #                        .set("es.port", "9200")
    #sc = SparkContext(appName=APP_NAME, conf=sparkConf)
    #spark = SparkSession(sc)
    #sc.setLogLevel("ERROR")




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

#** cast timestamp
    # Apply the machine learning model and select only the interesting casted columns
    df = model.transform(df) \
        .withColumn("latitude", df.latitude.cast(types.FloatType())) \
        .withColumn("longitude", df.longitude.cast(types.FloatType())) \
        .withColumn('location', array(col('latitude'), col('longitude'))) \
        .select("timestamp", "title", "publish_date", "predictedString", \
        "country_code", "location")


    df.writeStream\
    .foreachBatch(process_batch) \
    .start() \
    .awaitTermination()


    # write to elasticsearch (in batch)
    #df.writeStream \
    #    .option("checkpointLocation", "/save/location") \
    #    .format("es") \
    #    .start(elastic_index) \
    #    .awaitTermination()


if __name__ == "__main__":
    main()
















'''









print("Testing with a local dataframe: ", mlTestPath)
# load dataset
print("Reading test dataframe...")
test = spark.read.csv(mlTestPath, inferSchema=True, header=True, sep="\t")
print("... done.")
test.printSchema()

test = test.withColumn("text", concat_ws(" ", "title", "description")) # Add a new column 'text' by concatinating 'headline' and 'short_description'
test = test.select("_c0", "text") # Remove old text columns

# Prepare test documents, which are unlabeled (id, text) tuples.
#test = spark.createDataFrame([
#    (0, "Takeover benefits: UBS investors warm to Credit Suisse deal UBS's emergency takeover of Credit Suisse may lead to thousands of job losses, departures of key staff and a risky integration challenge, but for many UBS investors it increasingly looks like a good"),
#    (1, "John Lewis boss Sharon White: Criminals have a 'licence to shopflift' - Retail Gazette	John Lewis boss Sharon White has cautioned that criminals have a “licence to shoplift” following a rise in cases spurred by the cost-of-living crisis."),
#    (2, "Iraq, Syria leaders hold 1st talks in 12 years	DAMASCUS, Syria -- Iraq's prime minister met Sunday with Syrian President Bashar Assad in Damascus during the first trip of its kind to the war-torn country since the 12-year conflict began."),
#    (3, "Innovation Generation conference kicks off in Adelaide | PHOTOS | Stock Journal | SA Adelaide is hosting youthful growers from across the country for the three-day Innovation Generation conference hosted by GrainGrowers.")
#], ["id", "text"])

# Make predictions on test documents and print columns of interest.
prediction = pipelineFit.transform(test) \
    .select("_c0", "text", "probability", "predictedString")

prediction.show(100, truncate=False)

print("Local test finished. No more task. Ciaoooo!")
print("Starting streaming queries section...")
'''