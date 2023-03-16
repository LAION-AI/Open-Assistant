# Grafana

[Grafana](https://github.com/grafana/grafana) is used to visualize custom
observabiltiy metrics and much more.

This folder contains various configuration files for Grafana.

- [`./dashboards/dashboard.yaml`](./dashboards/dashboard.yaml) - Used to tell
  Grafana where some pre-configured dashboards live.
- [`./dashboards/fastapi-backend.json`](./dashboards/fastapi-backend.json) - A
  json representation of a saved Grafana dashboard focusing on some high level
  api endpoint metrics etc.
- [`./datasources/datasource.yml`](./datasources/datasource.yml) - A config file
  to set up Grafana to read from the local Prometheus source.
