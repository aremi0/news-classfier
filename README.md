# World News Classfier

## TODO:
- [x] Modificare il demone per fargli scaricare parte del database di GDELT, così da avere a fine pipeline quache milione di record in kibana.
- [ ] Modificare sparkExector in modo da fargli elaborare soltanto una volta i dataframe "vecchi", salvandoli magari in un volume convidiviso. Quindi dovrà soltanto inviare i dati già elaborati ad elasticsearch e poi elaborare qualli che arrivano in real-time.
- [ ] Eliminare la batch in elasticsearch facendogli mandare direttamente i dati a kibana.
- [x] Sistemare in elasticsearch/kibana il date format per usare il publish_date come riferimento temporale.
- [x] Aggiungere più info in kibana.
- [x] Migliorare la presentazione.
- [ ] Aggiungere altre visualizzazioni grafiche.
---  
Attualmente il demone scaricherà i dataframe del giorno odierno caricati fino all'istante in cui viene lanciato.  
Fluentd non ha la capacità di eliminare i file dopo la lettura, perciò bisognerà eliminare manualmente il volume "dataframe"

---
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
