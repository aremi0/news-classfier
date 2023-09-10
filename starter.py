import os 

build = input("Do you want to build all docker images? y/n\n")
if build == "y":
    os.system("docker build ./daemon --tag tap:daemon")
    os.system("docker build ./fluentd --tag tap:fluentd")
    os.system("docker build ./kafka --tag tap:kafka")
    os.system("docker build ./spark --tag tap:sparkP")
    os.system("docker build ./kibana --tag tap:kibana")
else:
    print("Do you want to run also sparkTrainer?")
    trainer = input("If this is the first time you execute type 'y' else type 'n'\n")

    if trainer == "y" :
        print("It will take a bit, pyspark set log-level('error') so there will be no log on terminal\n")
        os.system("docker compose -f ./withTrainer.yaml up")
    else :
        print("As you want...\n")
        os.system("docker compose -f ./withoutTrainer.yaml up")



# curl -f localhost:8080        #to see kafka-UI (broker status, topic, messages, ...)
# curl -f localhost:4040        #to see spark-cluster
# curl -f localhost:9200        #to see elasticsearch-cluster
# curl -f localhost:9200/news_index #to see elasticsearch index created in sparkExecutor
# curl -f localhost:5601 #for kibana data views

# docker run -it --entrypoint /bin/bash --volume news-classifier-tap_dataframe:/app/dataframe tap:daemon