print("_______________trainer____accuracy:96%____dataset:2225rows______________")

from pyspark.ml import Pipeline # pipeline to transform data
from pyspark.sql import SparkSession # to initiate spark
import pyspark.sql.types as types
from pyspark.sql.functions import concat_ws # to concatinate cols
from pyspark.ml.feature import StringIndexer, IndexToString # indexer
from pyspark.ml.feature import RegexTokenizer # tokenizer
from pyspark.ml.feature import HashingTF, IDF # vectorizer
from pyspark.ml.feature import StopWordsRemover # to remove stop words
from pyspark.ml.classification import LogisticRegression # ml model
from pyspark.ml.evaluation import MulticlassClassificationEvaluator # to evaluate the model
from pyspark.mllib.evaluation import MulticlassMetrics # performance metrics

trainingPath = "/opt/tap/training/5class"
datasetPath = "/opt/tap/dataset/bbc-news-data.csv"

# create a new spark session
spark = SparkSession.builder.master("local[*]")\
                            .appName("trainer")\
                            .getOrCreate()

# Reduce the verbosity of logging messages
#spark.setLogLevel("ERROR")

# load dataset
print("Reading training set...")
df = spark.read.csv(datasetPath, inferSchema=True, header=True, sep="\t")
print("... done.")
df.printSchema()


df = df.withColumn("text", concat_ws(" ", "title", "content")) # Add a new column 'text' by concatinating 'title' and 'content'
df = df.select("category", "text") # Remove old text columns

labelIndexer = StringIndexer(inputCol="category", outputCol="label").fit(df) # Mapping a string column of class/category to an ML column of label indices
#df = labelIndexer.transform(df)

tokenizer = RegexTokenizer(inputCol="text", outputCol="words", pattern="\\W") # Convert sentences to list of words
#df = tokenizer.transform(df)

stopwords_remover = StopWordsRemover(inputCol="words", outputCol="filtered") # To remove stop words like is, the, in, etc.
#df = stopwords_remover.transform(df)

hashing_tf = HashingTF(inputCol="filtered", outputCol="raw_features", numFeatures=10000) # Calculate term frequency in each article
#featurized_data = hashing_tf.transform(df)

idf = IDF(inputCol="raw_features", outputCol="features") # Inverse document frequency
#idf_vectorizer = idf.fit(featurized_data)

# Converting text to vectors
#rescaled_data = idf_vectorizer.transform(featurized_data)
# Split Train/Test data
#(train, test) = rescaled_data.randomSplit([0.75, 0.25], seed = 202)

# model object
lr = LogisticRegression(featuresCol='features',
                        labelCol='label',
                        family="multinomial",
                        regParam=0.3,
                        elasticNetParam=0,
                        maxIter=50)


#lrModel = lr.fit(train) # train model with default parameters

# Map back prediction labels to the equivalent category string
categoryConverter = IndexToString(inputCol="prediction", outputCol="predCategory", labels=labelIndexer.labels)


#predictions = lrModel.transform(test) # get predictions for test set



#predictions.select("text", 'probability','prediction', 'label').show() # show top 20 predictions
#evaluator = MulticlassClassificationEvaluator(predictionCol="prediction") # to evalute model
#print("______________-Test-set Accuracy is : ", evaluator.evaluate(predictions)) # print test accuracy

# Put everything in pipeline
pipeline = Pipeline(stages=[labelIndexer, tokenizer, stopwords_remover,
                            hashing_tf, idf, lr, categoryConverter])

# Fit the pipeline to training documents.
pipelineFit = pipeline.fit(df)


# Saving models in local on the mounted volume to be loaded later
pipelineFit.write().overwrite().save(trainingPath)
print("Pipeline trained => model saved on: ", trainingPath)
print("Task completed!")


#dataset.select("category", "prediction", "predCategory").show()

# take a random sample of 50 prediction
#rdd = dataset.select("category", "prediction", "predCategory").rdd

#rdd_sample = rdd.takeSample(withReplacement=False, num=50)
#print(rdd_sample)