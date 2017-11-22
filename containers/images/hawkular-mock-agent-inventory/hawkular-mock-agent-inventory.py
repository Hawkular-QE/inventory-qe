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
import json
import locust.events
from locust import HttpLocust, TaskSet, task
import uuid
from resources import Resources

# Resource types initialization should be independent of any client activity
global resources
resources = Resources()
Resources.add_resource_types(Resources.create_resource_types())


class AgentLifeCycle(TaskSet):
    def on_start(self):
        global feed
        self.feed_id = "feed-" + str(uuid.uuid4())
        feed = self.feed_id
        print "New Agent [%s]" % self.feed_id,
        self.agent_resources = resources.create_large_inventory(self.feed_id)
        with self.client.post("/import", json.dumps(self.agent_resources), headers=resources.get_headers()) as response:
            print "Agent [%s] - full auto-discovery" % self.feed_id

    @task
    def deploy_app(self):
        with self.client.post("/import",
                         json.dumps(Resources.create_app_resource(self.feed_id, self.feed_id + "-NewApp.war")), headers=resources.get_headers()) as response:
            print "Agent [%s] - deploys NewApp.war" % self.feed_id

    @task
    def undeploy_app(self):
        with self.client.delete("/resources/" + self.feed_id + "-NewApp.war", headers=resources.get_headers(),
                                catch_response=True) as response:
            print "Agent [%s] - undeploys NewApp.war" % self.feed_id


class HawkularAgent(HttpLocust):
    task_set = AgentLifeCycle
    host = resources.get_url()
    global execution
    execution = "execution" + str(uuid.uuid4())
    min_wait = resources.get_milliseconds_request()
    max_wait = resources.get_milliseconds_request()
    resources.create_database()

    def __init__(self):
        super(HawkularAgent, self).__init__()
        locust.events.request_success += self.hook_request_success
        locust.events.request_failure += self.hook_request_fail

    def hook_request_success(self, request_type, name, response_time, response_length):
        metrics = {}
        tags = {'execution': execution}
        metrics['measurement'] = "request"
        fields = {'request_type': request_type,
                  'request_increment': 1,
                  'agent': feed,
                  'response_time': response_time, 'response_length': response_length,
                  'name': name}
        metrics['fields'] = fields
        metrics['tags'] = tags
        resources.write_points([metrics])

    def hook_request_fail(self, request_type, name, response_time, exception):
        print "Agent [%s] - failed to " % feed + str(request_type) + " Exception: " + str(exception)

if __name__ == '__main__':
    agent = HawkularAgent()
    agent.run()
