FROM amazoncorretto:17
ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=3.4.0
ENV HADOOP_VERSION=hadoop3
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH

ADD setup/spark-${SPARK_VERSION}-bin-${HADOOP_VERSION}.tgz /opt

RUN yum -y update && yum install -y procps gcc openssl-devel bzip2-devel libffi-devel wget tar make
RUN yum -y install python3
RUN yum -y install glibc
RUN pip3 install pyspark numpy elasticsearch

#RUN pip3 -y uninstall urllib3
RUN pip3 install 'urllib3<2.0'

ADD code/requirements.txt /code/requirements.txt
RUN pip3 install -r /code/requirements.txt

RUN ln -s /opt/spark-${SPARK_VERSION}-bin-${HADOOP_VERSION} ${SPARK_DIR} 

ADD dataset /opt/tap/dataset
# Add Python Code
ADD code/*  /opt/tap/
# Mount in a docker volume to save/load ML trained pipeline models
RUN mkdir /opt/tap/training

# Add Spark Manager
ADD spark-manager.sh $SPARK_DIR/bin/spark-manager

WORKDIR ${SPARK_DIR}



# docker build . --tag tap:sparkP

# to run an interactive container for exploring the machine:
# docker run --entrypoint /bin/bash -v training:/opt/tap/training -it tap:sparkP