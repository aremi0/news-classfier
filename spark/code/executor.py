print("_______________executor________________")

from os.path import exists
import pyspark.sql.types as types
from pyspark.sql.functions import from_json, concat_ws
from pyspark.ml import PipelineModel
from pyspark.sql.session import SparkSession
#from elasticsearch import Elasticsearch

trainingPath = "/opt/tap/training/17class"

APP_NAME = 'news-classfier'
APP_BATCH_INTERVAL = 1

elastic_host="http://elasticsearch:9200"
elastic_index="news_es"
kafkaServer="kafkaServer:9092"
topic = "articles"



if not exists(trainingPath):
    print("Il modello non esiste, devi prima istruire un modello!")
    exit()


# elasticsearch section ------
#es = Elasticsearch(elastic_host, verify_certs=False)
# -------

# batch_df: results dataframe       <class 'pyspark.sql.dataframe.DataFrame'>
# batch_id: Batch0, Batch1, ...     <int>
def process_batch(batch_df, batch_id) :
    print("batch_df: ", type(batch_df), "_____size: ", batch_df.count())
    batch_df.show()
    print("batch_id: ", type(batch_id))
    print("___value: ", batch_id)
    batch_id.show()
    '''
    for idx, row in enumerate(batch_df.collect()) :
        row_dict = row.asDict()
        print(row_dict)
        id = f'{batch_id}-{idx}'
        resp = es.index(index=elastic_index, id=id, document=row_dict)
        print(resp)
    batch_df.show()
    '''



'''
 #   Column                 Non-Null Count  Dtype  
---  ------                 --------------  -----  
 0   Unnamed: 0             19 non-null     int64  
 1   EVENT_ID               19 non-null     int64  
 2   PUBLISH_DATE           19 non-null     int64  
 3   ActionGeo_CountryCode  19 non-null     object 
 4   ActionGeo_Lat          19 non-null     float64
 5   ActionGeo_Long         19 non-null     float64
 6   SOURCEURL              19 non-null     object 
 7   title                  19 non-null     object 
 8   text                   18 non-null     object 
'''

# spark section------
# Define articles schema structure
articlesSchema = types.StructType([
    types.StructField(name='_c0', dataType=types.StringType()),
    types.StructField(name='EVENT_ID', dataType=types.StringType()),
    types.StructField(name='PUBLISH_DATE', dataType=types.StringType()),
    types.StructField(name='ActionGeo_CountryCode', dataType=types.StringType()),
    types.StructField(name='ActionGeo_Lat', dataType=types.StringType()),
    types.StructField(name='ActionGeo_Long', dataType=types.StringType()),
    types.StructField(name='SOURCEURL', dataType=types.StringType()),
    types.StructField(name='title', dataType=types.StringType()),
    types.StructField(name='text', dataType=types.StringType()),
])

# create a new spark session
spark = SparkSession.builder.master("local[*]")\
                            .appName(APP_NAME)\
                            .getOrCreate()
spark.sparkContext.setLogLevel("ERROR") # Reduce the verbosity of logging messages

print("Loading pre-trained model from: ", trainingPath, "...")
model = PipelineModel.load(trainingPath)
print("... loaded.")
# ------

# Streaming Query section ------
print("Reading stream from kafka...")
# Read the stream from kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("startingOffsets", "earliest") \
    .option("subscribe", topic) \
    .option("includeHeaders", "true") \
    .load()

# Cast the message received from kafka with the provided schema
df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", articlesSchema).alias("data")) \
    .select("data.*")

# Apply the machine learning model and select only the interesting columns
results = model.transform(df) \
    .select("title", "PUBLISH_DATE", "predictedString", "ActionGeo_CountryCode", \
            "ActionGeo_Lat", "ActionGeo_Long")

print("___SCHEMA")
results.printSchema()
print("___ENTRIES")

'''
# Write the stream to elasticsearch
result.writeStream \
    .format("console") \
    .outputMode("append") \
    .start() \
    .awaitTermination()
'''

results.writeStream\
.foreachBatch(process_batch) \
.start() \
.awaitTermination()

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