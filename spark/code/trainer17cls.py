# 17 classi non ambigue => 125.000 text di esercitazione con df splittato al 85%
# Naive Bayes con parametri defalt => numFeatures ottimale 250.000
# accuracy massima ottenuta 72.5%

print("__________trainer_17_NaiveBayes__________")

from pyspark.ml import Pipeline # pipeline to transform data
from pyspark.sql import SparkSession, SQLContext # to initiate spark
from pyspark.sql.functions import concat_ws, when, regexp_replace
from pyspark.ml.feature import StringIndexer, IndexToString # indexer
from pyspark.ml.feature import RegexTokenizer # tokenizer
from pyspark.ml.feature import HashingTF, IDF # vectorizer
from pyspark.ml.feature import StopWordsRemover # to remove stop words
from pyspark.ml.classification import NaiveBayes # ml model
from pyspark.ml.evaluation import MulticlassClassificationEvaluator # to evaluate the model
from pyspark.mllib.evaluation import MulticlassMetrics # # performance metrics


trainingPath = "/opt/tap/training/17class"
datasetPath = "/opt/tap/dataset/*.json"

# Remaining class: sports, politics, entertainment, environment, tech, business, style&beauty, 
# religion, education, travel, crime, rights, food&drink, arts&colture, world-news, science, wellness
def dataframeCleaner(df) :
    # Removing ambiguous category's rows
    rows_to_delete = df.filter(df.category.contains("THE WORLDPOST") |\
                                df.category.contains("PARENTING") |\
                                df.category.contains("GREEN") |\
                                df.category.contains("U.S. NEWS") |\
                                df.category.contains("MONEY") |\
                                df.category.contains("IMPACT") |\
                                df.category.contains("WEDDINGS") |\
                                df.category.contains("HOME & LIVING") |\
                                df.category.contains("TASTE") |\
                                df.category.contains("FIFTY") |\
                                df.category.contains("WEIRD NEWS") |\
                                df.category.contains("WORLDPOST") |\
                                df.category.contains("GOOD NEWS") |\
                                df.category.contains("HEALTHY LIVING") |\
                                df.category.contains("PARENTS") |\
                                df.category.contains("MEDIA") |\
                                df.category.contains("COLLEGE") |\
                                df.category.contains("WOMEN") |\
                                df.category.contains("DIVORCE"))
    df = df.join(rows_to_delete, on=["category"], how='left_anti')

    # Pouring correlated categories into a less specific category
    df = df.withColumn("category", when(df.category.contains("BLACK VOICES") |\
                                        df.category.contains("QUEER VOICES") |\
                                        df.category.contains("LATINO VOICES"), \
                                        "RIGHTS").otherwise(df["category"]))
    df = df.withColumn("category", when(df.category.contains("ARTS"), \
                                        "ARTS & CULTURE").otherwise(df["category"]))
    df = df.withColumn("category", when(df.category.contains("STYLE"), \
                                        "STYLE & BEAUTY").otherwise(df["category"]))
    df = df.withColumn("category", when(df.category.contains("COMEDY"), \
                                        "ENTERTAINMENT").otherwise(df["category"]))

    df = df.withColumn("text", concat_ws(" ", "headline", "short_description")) # Add a new column 'text' by concatinating 'headline' and 'short_description'
    df = df.select("category", "text") # Remove old text columns

    df = df.select(regexp_replace("category", "[^a-zA-Z0-9]+", "").alias("category"), \
                    regexp_replace("text", "[^a-zA-Z0-9\s]+", "").alias("text")) # Replace all the not (^) specified char with empty (will replace special char)

    return df

def printCategory(spark, df) :
    # to print all categories classes
    sqlContext = SQLContext(spark)
    df.createOrReplaceTempView("newsgroups")
    results = sqlContext.sql("SELECT DISTINCT category FROM newsgroups")
    results.show(results.count(), False)
    print("___There are: ", results.count(), " class...")

    #exit(0)

def main() :
    # create a new spark session
    spark = SparkSession.builder.master("local[*]")\
                                .appName("news classfier")\
                                .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR") # Reduce the verbosity of logging messages

    # load dataset
    print("Reading training set...")
    df = spark.read.json(datasetPath)
    print("... done.")
    df.printSchema()

    df = dataframeCleaner(df)

    printCategory(spark, df)

    labelIndexer = StringIndexer(inputCol="category", outputCol="label").fit(df) # Mapping a string column of class/category to an ML column of label indices
    #df = labelIndexer.transform(df)

    tokenizer = RegexTokenizer(inputCol="text", outputCol="words", pattern="\\W") # Convert sentences to list of words
    #df = tokenizer.transform(df)
    
    eng=StopWordsRemover.loadDefaultStopWords("english")
    stopwords_remover = StopWordsRemover(inputCol="words", outputCol="filtered", stopWords=eng)
    #df = stopwords_remover.transform(df)

    hashing_tf = HashingTF(inputCol="filtered", outputCol="raw_features", numFeatures=250000)
    #featurized_data = hashing_tf.transform(df)

    idf = IDF(inputCol="raw_features", outputCol="features")
    #idf_vectorizer = idf.fit(featurized_data)

    #rescaled_data = idf_vectorizer.transform(featurized_data)

    #(train, test) = df.randomSplit([0.85, 0.15], seed = 202)
    
    
    nb = NaiveBayes(modelType="multinomial")
    #nbModel = nb.fit(train)
    #predictions = nbModel.transform(test) # get predictions for test set

    categoryConverter = IndexToString(inputCol="prediction", outputCol="predictedString", labels=labelIndexer.labels)



    pipeline = Pipeline(stages=[labelIndexer, tokenizer, stopwords_remover,
                                hashing_tf, idf, nb, categoryConverter])
    pipelineFit = pipeline.fit(df)

    # Saving models in local on the mounted volume to be loaded later
    pipelineFit.write().overwrite().save(trainingPath)
    print("Pipeline trained => model saved on: ", trainingPath)
    print("Task completed!")

    #-----------
    # If you want to test accuracy:
    #pipelineFit = pipeline.fit(train)

    # show top 20 predictions
    #predictions = pipelineFit.transform(test)
    #predictions.select("prediction", "label").show()

    # to evalute model
    #evaluator = MulticlassClassificationEvaluator(
    #    labelCol="label", predictionCol="prediction", metricName="accuracy")

    #accuracy = evaluator.evaluate(predictions)
    #print("______________-Test-set Accuracy is : ", evaluator.evaluate(predictions)) # print test accuracy
    #-----------



if __name__ == "__main__":
    main()
    print("____Task finished!____")



