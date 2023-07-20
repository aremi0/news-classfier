FROM docker.elastic.co/logstash/logstash:8.2.0

# Add your logstash plugins setup here
RUN logstash-plugin install logstash-filter-sentimentalizer logstash-codec-csv

# Mount in a docker volume to load dataframe
RUN mkdir /usr/share/logstash/dataframe

# docker build . --tag tap:logstash
