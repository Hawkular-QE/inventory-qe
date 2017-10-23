FROM python:2.7

# Copy the application's requirements.txt and run pip to install all
ADD requirements.txt  requirements.txt
RUN pip install -r requirements.txt

COPY resources.py .
COPY hawkular-mock-agent-inventory.py .

CMD locust -f hawkular-mock-agent-inventory.py --host ${HAWKULAR_INVENTORY_URL} -c 1000  --print-stats --no-web
