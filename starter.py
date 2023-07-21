import os 

build = input("Do you want to build all docker images? y/n\n")
if build == "y":
    os.system("docker build ./daemon --tag tap:daemon")
    os.system("docker build ./logstash --tag tap:logstash")
    #os.system("docker build ./kafka --tag tap:kafka")
    os.system("docker build ./spark --tag tap:sparkP")
    os.system("docker build ./kibana --tag tap:kibana")
else:
    print("Do you want to run also sparkTrainer?")
    trainer = input("If this is the first time you execute type 'y' else type 'n'\n")

    if trainer == "y" :
        print("It will take a bit, pyspark set log-level('error') so there will be no log on terminal\n")
        os.system("docker compose -f ./withTrainer up")
    else :
        print("As you want...\n")
        os.system("docker compose -f ./withoutTrainer.yaml up")



# localhost:8080 to see kafka-UI (broker status, topic, messages, ...)
# localhost:4040 to see spark-cluster
# localhost:9200 to see elasticsearch-cluster
# localhost:9200/news_es to see elasticsearch index created in sparkExecutor
# localhost:5601 for kibana data views