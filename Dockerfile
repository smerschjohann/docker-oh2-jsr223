FROM openhab/openhab:2.5.0-debian
MAINTAINER Simon Merschjohann <smerschjo@gmail.com>

ENV CLASSPATH /opt/jython/jython.jar
ENV EXTRA_JAVA_OPTS " -Dpython.home=/opt/jython -Dpython.path=/openhab/userdata/automation/pylib "

RUN cd /tmp && wget http://central.maven.org/maven2/org/python/jython-installer/2.7.1/jython-installer-2.7.1.jar \
    && java -jar /tmp/jython-installer-2.7.1.jar -s -d /opt/jython -t standard -e demo doc src \
    && rm /tmp/jython-installer-2.7.1.jar \
    && wget --no-check-certificate https://cdn.azul.com/zcek/bin/ZuluJCEPolicies.zip \
    && unzip -jo -d ${JAVA_HOME}/jre/lib/security /tmp/ZuluJCEPolicies.zip \
    && rm /tmp/ZuluJCEPolicies.zip

RUN apt update && apt -y install openssh-client && apt-get clean
