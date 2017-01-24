FROM openhab/openhab:amd64

ENV CLASSPATH /opt/jython/jython.jar
ENV EXTRA_JAVA_OPTS " -Dpython.home=/opt/jython -Dpython.path=/openhab/userdata/automation/pylib "


RUN rm -r /openhab/runtime/system/org/eclipse/smarthome/automation && cd /tmp && wget http://central.maven.org/maven2/org/python/jython-installer/2.7.1b3/jython-installer-2.7.1b3.jar \
    && java -jar /tmp/jython-installer-2.7.1b3.jar -s -d /opt/jython -t standard -e demo doc src \
    && rm /tmp/jython-installer-2.7.1b3.jar \
    && wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jce/8/jce_policy-8.zip \
    && unzip -jo -d ${JAVA_HOME}/jre/lib/security /tmp/jce_policy-8.zip \
    && rm /tmp/jce_policy-8.zip
    
RUN apt update && apt -y install openssh-client && apt-get clean
