# World News Classfier
This project aim to collect, analyze and classify webnews from all over the world and clearly display the processed data in organized dashboards.

Every specific aspects of the project, in each of its parts, are explained in the documentation (in Italian). In addition, the source code is properly commented (in English).

[Documentation](./book/presentation.ipynb)
---

### How to start this project
First of all [Docker](https://www.docker.com/) need to be installed on your machine.

1. Clone this repo
2. If you have python just launch:  
`$ python starter.py`  
otherwise:
```
$ docker build ./daemon --tag tap:daemon
$ docker build ./fluentd --tag tap:fluentd
$ docker build ./kafka --tag tap:kafka
$ docker build ./spark --tag tap:sparkP
$ docker build ./kibana --tag tap:kibana

and then
$ docker compose -f withTrainer.yaml up
or
$ docker compose -f withoutTrainer.yaml up
``` 

<details>
    <summary style="font-size:10px">other details</summary>
    Con i broccoli in padella si va sempre sul sicuro. Si tratta infatti di un contorno di stagione sfizioso e saporito che si presta a varie combinazioni. Grazie al loro gusto, deciso ma delicato allo stesso tempo, sono un accompagnamento ideale a secondi piatti di carne o di pesce, in particolar modo il baccalà. Per una cena più leggera e veloce sono ottimi anche con i formaggi e le uova.
    Abbinati alle salsicce costituiscono un gustoso secondo piatto, ma anche una coppia vincente per condire la pasta o farcire rustiche torte salate. I broccoletti in padella sono una pietanza tanto versatile da risultare imprescindibile.
    In questa ricetta vi proponiamo di far saltare le cimette dei broccoli. La parte più dura dei gambi e le foglie sono preziosi ingredienti per la preparazione di minestre o passati di verdura.
    Se amate questa deliziosa varietà di cruciferae, ricca di elementi nutritivi e vitamina C, approfittatene ora che la stagione è iniziata. Le ricette con i broccoli sono svariate, potete passare con gusto da una Crema di broccoli al latte di cocco alle Polpette, senza lasciarvi sfuggire la Quiche di patate con cavolfiori, caciotta e broccoli o i Ravioli di sfoglia con crema di broccoli e acciughe.
</details>