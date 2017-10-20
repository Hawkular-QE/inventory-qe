"""
Copyright 2015-2017 Red Hat, Inc. and/or its affiliates
and other contributors as indicated by the @author tags.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

author Lucas Ponce

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
"""
import json
from locust import HttpLocust, TaskSet, task
import uuid
from resources import Resources

# Inventory base url
# [todo] This should be defined from environment properties
global inventory_url
inventory_url = 'http://localhost:8080/hawkular/inventory'

# Resource types initialization should be independent of any client activity
global resources
resources = Resources()
Resources.add_resource_types(inventory_url, Resources.create_resource_types())

global headers
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

class AgentLifeCycle(TaskSet):
    def on_start(self):
        self.feed_id = "feed-" + str(uuid.uuid4())
        print "New Agent [%s]" %  self.feed_id,
        # Simulating 1 server with 99 children resources each one with 20 metrics, so 100 resources per agent
        self.agent_resources = resources.create_large_inventory(self.feed_id, 1, 99, 20)

    @task
    class ImportFullInventory(TaskSet):
        @task
        def import_agent_inventory(self):
            print "Agent [%s] is importing inventory" % self.parent.feed_id,
            self.client.post("/import", json.dumps(self.parent.agent_resources), headers=headers)

class HawkularAgent(HttpLocust):
    task_set = AgentLifeCycle
    host = inventory_url
    min_wait = 1000
    max_wait = 1000
