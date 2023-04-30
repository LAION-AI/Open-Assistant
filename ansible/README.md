To test the ansible playbook on localhost run
`ansible-playbook -i test.inventory.ini dev.yaml`.\
In case you're missing the ansible docker dependency install it with `ansible-galaxy collection install community.docker`.\
Point Redis Insights to the Redis database by visiting localhost:8001 in a
browser and select "I already have a database" followed by "Connect to a Redis
Database".\
For host, port and name fill in `oasst-redis`, `6379` and `redis`.
