FROM fluentd

USER root

RUN mkdir /fluentd/dataframe

RUN apk update && apk add ruby-dev

RUN fluent-gem install fluent-plugin-kafka fluent-plugin-elasticsearch