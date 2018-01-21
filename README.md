# Prometheus exporter for Slushpool

## Installation

Just execute the python script. Ensure that you have Python-Tornado installed

## Usage

./slush_exporter.py

## Configuration

There is no configuration required

Service runs on port 9155

Testing can be done by loading /metrics?token=<SLUSH API TOKEN>

example:

curl hlocalhost:9154:/metrics?target=192.168.0.21

## Prometheus configuration

Configuration Example

Setup the targets array with your miners, and set the replacement line to the host running the exporter:

```YAML
- job_name: 'antminer'
    scrape_interval: 2s
    static_configs:
      - targets: ['192.168.0.21', '192.168.0.22', '192.168.0.23', '192.168.0.24']
    metrics_path: /metrics
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 192.168.0.190:9154
```

This setup allows Prometheus to provide scheduling and service discovery, as
unlike all other exporters running an exporter on the machine from which we are
getting the metrics from is not possible.

## Docker

A Docker container has been built and is available at Dockerhub: majestik/cgminer_exporter
