"""
Copyright 2015-2017 Red Hat, Inc. and/or its affiliates
and other contributors as indicated by the @author tags.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

author Lucas Ponce
author Guilherme Baufaker Rego

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
"""
import base64
import json
import os

import requests
from influxdb import InfluxDBClient


class Resources (object):

    def __init__(self):
        self.influxClient = InfluxDBClient(
        **{'host': os.environ['INFLUX_HOST'], 'username': os.environ['INFLUX_USERNAME'],
           'port': os.environ['INFLUX_PORT'], 'database': os.environ['INFLUX_DATABASE'],
           'password': os.environ['INFLUX_PASSWORD']})

    @staticmethod
    def get_headers():
        headers = {'Content-type': 'application/json', 'Accept': 'application/json',
                   'Authorization': "Basic %s" % base64.b64encode(os.environ['HAWKULAR_USERNAME'] + ":" + os.environ[
                       'HAWKULAR_PASSWORD'])
                   }
        return headers

    @staticmethod
    def get_milliseconds_request():
        try:
            milliseconds = int(os.environ['MILLISECONDS_REQUEST'])
        except KeyError:
            milliseconds = 5000
        return milliseconds

    @staticmethod
    def get_url():
        try:
            url = os.environ['HAWKULAR_HOST']
        except KeyError:
            url = 'http://localhost'
        try:
            port = os.environ['HAWKULAR_PORT']
        except KeyError:
            port = "8080"
        inventory_path = "/hawkular/inventory"
        return url + ":" + port + inventory_path

    @staticmethod
    def create_resource_types():
        reload = {
            'param1': {
                'type': 'bool',
                'description': 'Description of param1 for Reload op'
            },
            'param2': {
                'type': 'bool',
                'description': 'Description of param2 for Reload op'
            }
        }
        shutdown = {
            'param1': {
                'type': 'bool',
                'description': 'Description of param1 for Shutdown op'
            },
            'param2': {
                'type': 'bool',
                'description': 'Description of param2 for Shutdown op'
            }
        }
        flush = {
            'param1': {
                'type': 'bool',
                'description': 'Description of param1 for Flush op'
            },
            'param2': {
                'type': 'bool',
                'description': 'Description of param2 for Flush op'
            }
        }

        eap = {
            'id': 'EAP',
            'operations': [
                {
                    'name': 'Reload',
                    'parameters': reload
                },
                {
                    'name': 'Shutdown',
                    'parameters': shutdown
                },
                {
                    'name': 'Start',
                    'parameters': {}
                }
            ],
            'properties': {
                'eapProp1': 'eapVal1',
                'eapProp2': 'eapVal2',
                'eapProp3': 'eapVal3'
            }
        }
        jdg = {
            'id': 'JDG',
            'operations': [
                {
                    'name': 'Flush',
                    'parameters': flush
                },
                {
                    'name': 'Delete',
                    'parameters': {}
                }
            ],
            'properties': {
                'jdgProp1': 'jdgVal1',
                'jdgProp2': 'jdgVal2',
                'jdgProp3': 'jdgVal3'
            }
        }
        return [eap, jdg]

    @staticmethod
    def create_large_inventory(feed_id):
        # Number of Server
        try:
            num_resources = int(os.environ['NUMBER_OF_SERVERS'])
        except KeyError:
            num_resources = 1

        # Number of Children
        try:
            num_children = int(os.environ['NUMBER_OF_CHILDREN'])
        except KeyError:
            num_children = 99

        # Number of Metrics
        try:
            num_metrics = int(os.environ['NUMBER_OF_METRICS'])
        except KeyError:
            num_metrics = 20

        resources = []
        metrics = []
        for k in range(num_metrics):
            metric = {
                'name': "metric-" + str(k),
                'type': "Metric " + str(k),
                'unit': 'BYTES',
                'properties': {
                    'prop1': 'val1',
                    'prop2': 'val2'
                }
            }
            metrics.append(metric)

        for i in range(num_resources):
            type_id = "EAP" if (i % 2 == 0) else "JDG"
            id = feed_id + "-Server-" + str(i)
            name = "Server " + type_id + " with Id " + id
            for j in range(num_children):
                child_type = "FOO" if (i % 2 == 0) else "BAR"
                child_id = id + "-child-" + str(j)
                child_name = "Child " + str(j) + " from " + id
                child = {
                    'id': child_id,
                    'name': child_name,
                    'feedId': feed_id,
                    'typeId': child_type,
                    'parentId': id,
                    'metrics': metrics,
                    'properties': {
                        'prop1': 'val1',
                        'prop2': 'val2',
                        'description': "This is a description for " + child_id
                    },
                    'config': {
                        'confProp1': 'confValue1',
                        'confProp2': 'confValue2'
                    }
                }
                resources.append(child)

            server = {
                'id': id,
                'name': name,
                'feedId': feed_id,
                'typeId': type_id,
                'metrics': metrics,
                'properties': {
                    'prop1': 'val1',
                    'prop2': 'val2',
                    'description': "This is a description for " + id
                },
                'config': {
                    'confProp1': 'confValue1',
                    'confProp2': 'confValue2'
                }
            }
            resources.append(server)

        return {
            'resources': resources,
            'types': []
        }

    @staticmethod
    def add_resource_types(resource_types):
        import_types = {
            'resources': [],
            'types': resource_types
        }
        response = requests.post(Resources.get_url() + '/import', json.dumps(import_types), headers=Resources.get_headers())
        print "Imported resource types [%d]" % response.status_code,

    @staticmethod
    def create_app_resource(feed_id, app_id):
        """

        :rtype: object
        """
        app = {
            'id': app_id,
            'name': "New Application",
            'feedId': feed_id,
            'typeId': "Application",
            'metrics': [
                {'name': 'MetricA', 'type': 'TypeA', 'unit': 'BYTES'},
                {'name': 'MetricB', 'type': 'TypeB', 'unit': 'BYTES'}
            ],
            'properties': {
                'prop1': 'val1',
                'prop2': 'val2',
                'description': "This is a description for New Application"
            },
            'config': {
                'confProp1': 'confValue1',
                'confProp2': 'confValue2'
            }
        }

        return {
            'resources': [app],
            'types': []
        }

    def create_database(self):
        return self.influxClient.query("CREATE DATABASE " + os.environ['INFLUX_DATABASE'])

    def write_points(self, metrics):
        return self.influxClient.write_points(metrics)

