FROM hawkular/hawkular-services:hawkular-1275

USER root


RUN echo 'JAVA_OPTS="$JAVA_OPTS -Dhawkular.agent.metrics.host=0.0.0.0"' >> $JBOSS_HOME/bin/standalone.conf
