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
