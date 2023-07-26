Il dataframe consiste in un file CSV contenente le seguenti colonne/informazioni:
GLOBALEVENTID
SQLDATE
MonthYear
Year
FractionDate
Actor1Code
Actor1Name
Actor1CountryCode
Actor1KnownGroupCode
Actor1EthnicCode
Actor1Religion1Code
Actor1Religion2Code
Actor1Type1Code
Actor1Type2Code
Actor1Type3Code
Actor2Code
Actor2Name
Actor2CountryCode
Actor2KnownGroupCode
Actor2EthnicCode
Actor2Religion1Code
Actor2Religion2Code
Actor2Type1Code
Actor2Type2Code
Actor2Type3Code
IsRootEvent
EventCode
EventBaseCode
EventRootCode
QuadClass
GoldsteinScale
NumMentions
NumSources
NumArticles
AvgTone
Actor1Geo_Type
Actor1Geo_FullName
Actor1Geo_CountryCode
Actor1Geo_ADM1Code
Actor1Geo_Lat
Actor1Geo_Long
Actor1Geo_FeatureID
Actor2Geo_Type
Actor2Geo_FullName
Actor2Geo_CountryCode
Actor2Geo_ADM1Code
Actor2Geo_Lat
Actor2Geo_Long
Actor2Geo_FeatureID
ActionGeo_Type
ActionGeo_FullName
ActionGeo_CountryCode
ActionGeo_ADM1Code
ActionGeo_Lat
ActionGeo_Long
ActionGeo_FeatureID
DATEADDED
SOURCEURL

Il demone ha il compito di interrogare ogni 15 minuti (tempo di update della sorgente) l'url della sorgente al fine di ottenere
ad ogni iterazione del loop l'ultimo dataframe caricato.
Molte delle voci del dataframe calcolate tramite machine learning risultano imprecise o null.
===> Risolto estraendo esclusivamente le colonne non-null più rilevanti per il progetto, il resto lo otterrò con scraping e MLlib

Il dataframe consiste in un  file CSV malformattato che causa problemi durante il reading
(sia in python che aprendolo con un normale programma).
===> Risolto con la violenza.

Ogni sito è strutturato in maniera differente, il che è un problema per lo scraping.
===> Risolto filtrando soltanto i siti con una determinata struttura.

sparkTrainer  | +--------------+
sparkTrainer  | |category      |
sparkTrainer  | +--------------+
sparkTrainer  | |SPORTS        |
sparkTrainer  | |POLITICS      |
sparkTrainer  | |ENTERTAINMENT |
sparkTrainer  | |ENVIRONMENT   |
sparkTrainer  | |TECH          |
sparkTrainer  | |BUSINESS      |
sparkTrainer  | |STYLE & BEAUTY|
sparkTrainer  | |RELIGION      |
sparkTrainer  | |EDUCATION     |
sparkTrainer  | |TRAVEL        |
sparkTrainer  | |CRIME         |
sparkTrainer  | |RIGHTS        |
sparkTrainer  | |FOOD & DRINK  |
sparkTrainer  | |ARTS & CULTURE|
sparkTrainer  | |WORLD NEWS    |
sparkTrainer  | |SCIENCE       |
sparkTrainer  | |WELLNESS      |
sparkTrainer  | +--------------+
sparkTrainer  | 
sparkTrainer  | 
sparkTrainer  | ___There are:  17  class...


Prediction accuracy: 74.5%