FROM hawkular/hawkular-services:latest

EXPOSE 5556 5555

USER root

# Set up the Prometheus endpoint for monitoring
RUN cd $JBOSS_HOME/bin && \
    curl -Lo $JBOSS_HOME/bin/jmx_prometheus_javaagent.jar https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.9/jmx_prometheus_javaagent-0.9.jar

ADD prometheus.yaml ${JBOSS_HOME}/configuration/prometheus.yaml

RUN echo 'JAVA_OPTS="$JAVA_OPTS -Djboss.modules.system.pkgs=org.jboss.byteman,org.jboss.logmanager -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.port=5555 -Djava.util.logging.manager=org.jboss.logmanager.LogManager -javaagent:$JBOSS_HOME/bin/jmx_prometheus_javaagent.jar=5556:${JBOSS_HOME}/configuration/prometheus.yaml"' >> $JBOSS_HOME/bin/standalone.conf
