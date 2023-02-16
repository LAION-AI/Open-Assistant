# Netdata

[Netdata](https://github.com/netdata/netdata) is an open source monitoring tool.

This folder contains some configfuration files used to set up various netdata
collectors we want to use like Redis, Postgres, etc.

- [`./go.d/postgres.conf`](./go.d/postgres.conf) - Config for Netdata
  [Postgres Collector](https://learn.netdata.cloud/docs/agent/collectors/go.d.plugin/modules/postgres).
- [`./go.d/prometheus.conf`](./go.d/prometheus.conf) - Config for Netdata
  [Prometheus Collector](https://learn.netdata.cloud/docs/agent/collectors/go.d.plugin/modules/prometheus).
- [`./go.d/redis.conf`](./go.d/redis.conf) - Config for Netdata
  [Redis Collector](https://learn.netdata.cloud/docs/agent/collectors/go.d.plugin/modules/redis).
