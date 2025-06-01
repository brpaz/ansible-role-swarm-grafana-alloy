
# Ansible Role: Grafana Alloy

> An Ansible role to deploy [Grafana Alloy](https://grafana.com/docs/alloy/latest/) monitoring stack in a Docker Swarm cluster.

## Features

- Deploys Grafana Alloy as a Docker Swarm service
- Supports multiple integrations (Node Exporter, Docker, Traefik, Redis, PostgreSQL)
- Configurable Prometheus recording and alerting rules

## Requirements

- Ansible 2.10 or higher
- Docker Swarm cluster
- Python Docker SDK (`python3-docker`)


## Installation

### Using Ansible Galaxy

You can install this role directly from Ansible Galaxy:

```bash
ansible-galaxy install brpaz.swarm_grafana_alloy
```

### Using requirements.yml

For version-controlled, repeatable role installations, add to your `requirements.yml`:

```yaml
---
roles:
  - name: brpaz.swarm_grafana_alloy
    version: v1.0.0  # Specify the version you want

collections:
  - name: community.docker
```

Then install with:

```bash
ansible-galaxy install -r requirements.yml
```

### Manual Installation

Alternatively, you can clone the repository directly:

```bash
# Create a roles directory if it doesn't exist
mkdir -p ~/.ansible/roles
# Clone the repository
git clone https://github.com/brpaz/ansible-role-swarm-grafana-alloy.git ~/.ansible/roles/brpaz.swarm_grafana_alloy
```

## Role Variables

### Main Configuration

| Variable                    | Description                          | Default Value              |
| --------------------------- | ------------------------------------ | -------------------------- |
| `alloy_cluster_name`        | Name of your cluster                 | `"my-cluster"`             |
| `alloy_config_dir`          | Configuration directory              | `/etc/alloy`               |
| `alloy_image`               | Alloy Docker image to use            | `grafana/alloy:v1.8.4`     |
| `alloy_swarm_service_name`  | Name of the Docker service           | `"alloy"`                  |
| `alloy_swarm_networks`      | List of Docker networks to attach to | `[{"name": "monitoring"}]` |
| `alloy_swarm_labels`        | Docker service labels                | See below                  |
| `alloy_reservations_cpus`   | CPU reservations                     | `0.5`                      |
| `alloy_reservations_memory` | Memory reservations                  | `256M`                     |
| `alloy_limits_cpus`         | CPU limits                           | `1.0`                      |
| `alloy_limits_memory`       | Memory limits                        | `512M`                     |
| `alloy_server_port`         | Server listening port                | `12345`                    |
| `alloy_log_level`           | Logging level                        | `"info"`                   |
| `alloy_log_format`          | Logging format                       | `"json"`                   |

Default service labels:
```yaml
alloy_swarm_labels:
  com.grafana.alloy.version: "v1.8.4"
  com.grafana.alloy.component: "monitoring"
  com.grafana.alloy.description: "Grafana Alloy monitoring agent"
```

### Remote Write Configuration

| Variable                 | Description                     | Default Value                                                  |
| ------------------------ | ------------------------------- | -------------------------------------------------------------- |
| `alloy_metrics_url`      | Metrics remote write URL        | `"https://prometheus-us-central1.grafana.net/api/prom/push"`   |
| `alloy_metrics_username` | Metrics authentication username | `""`                                                           |
| `alloy_metrics_password` | Metrics authentication password | `""`                                                           |
| `alloy_logs_url`         | Logs remote write URL           | `"https://logs-prod-us-central1.grafana.net/loki/api/v1/push"` |
| `alloy_logs_username`    | Logs authentication username    | `""`                                                           |
| `alloy_logs_password`    | Logs authentication password    | `""`                                                           |

### Integration Configuration

| Variable                                           | Description                      | Default Value    |
| -------------------------------------------------- | -------------------------------- | ---------------- |
| `alloy_integrations_node_exporter_enabled`         | Enable Node Exporter integration | `true`           |
| `alloy_integrations_node_exporter_scrape_interval` | Node Exporter scrape interval    | `"30s"`          |
| `alloy_integrations_docker_enabled`                | Enable Docker integration        | `true`           |
| `alloy_integrations_traefik_enabled`               | Enable Traefik integration       | `false`          |
| `alloy_integrations_traefik_address`               | Traefik metrics endpoint address | `"traefik:8080"` |
| `alloy_integrations_traefik_metrics_path`          | Traefik metrics path             | `"/metrics"`     |
| `alloy_integrations_traefik_scrape_interval`       | Traefik scrape interval          | `"30s"`          |
| `alloy_integrations_redis_enabled`                 | Enable Redis integration         | `false`          |
| `alloy_integrations_redis_address`                 | Redis address                    | `"redis:6379"`   |
| `alloy_integrations_redis_scrape_interval`         | Redis scrape interval            | `"30s"`          |
| `alloy_integrations_postgres_enabled`              | Enable PostgreSQL integration    | `false`          |
| `alloy_integrations_postgres_datasource_names`     | PostgreSQL datasource names      | `[]`             |
| `alloy_integrations_postgres_scrape_interval`      | PostgreSQL scrape interval       | `"30s"`          |
```

### Prometheus Rules Configuration

```yaml
# Recording rules
alloy_recording_rules:
  - record: "instance:node_cpu:rate5m"
    expr: "rate(node_cpu_seconds_total{mode='idle'}[5m])"
    labels:
      env: "production"

# Alerting rules
alloy_alert_rules:
  - alert: "HighCPUUsage"
    expr: "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode='idle'}[5m])) * 100) > 80"
    for: "5m"
    labels:
      severity: "warning"
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "CPU usage is above 80% for 5 minutes"
```

### Environment Variables

```yaml
# Optional environment variables for the Alloy service
alloy_environment_variables:
  ALLOY_LOG_FORMAT: "logfmt"
  ALLOY_LOG_LEVEL: "debug"
```

## Example Playbook

```yaml
- hosts: swarm_managers
  become: true
  roles:
    - role: brpaz.swarm_grafana_alloy
      vars:
        alloy_cluster_name: "production"
        alloy_swarm_networks:
          - name: "monitoring"
        alloy_integrations_node_exporter_enabled: true
        alloy_integrations_docker_enabled: true
        alloy_integrations_traefik_enabled: true
        alloy_integrations_traefik_address: "traefik:8080"
        alloy_metrics_username: "your-metrics-username"
        alloy_metrics_password: "your-metrics-password"
        alloy_logs_username: "your-logs-username"
        alloy_logs_password: "your-logs-password"
```

## Custom Integrations

To add a custom integration, place a `.alloy` file in the `/etc/alloy/` directory on the target host and restart the Alloy service. Check the [Alloy documentation](https://grafana.com/docs/alloy/latest/reference/components/) for more details.

## Testing

The role includes Molecule tests. To run them:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
molecule test
```

## Role Dependencies

- [community.docker](https://docs.ansible.com/ansible/latest/collections/community/docker/index.html) collection

## Contribute

All contributions are welcome. Please check [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 🫶 Support

If you find this project helpful and would like to support its development, there are a few ways you can contribute:

[![Sponsor me on GitHub](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23db61a2.svg?&logo=github&logoColor=red&&style=for-the-badge&labelColor=white)](https://github.com/sponsors/brpaz)

<a href="https://www.buymeacoffee.com/Z1Bu6asGV" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

## License

This project is MIT Licensed [LICENSE](LICENSE)

## 📩 Contact

✉️ **Email** - [oss@brunopaz.dev](oss@brunopaz.dev)

🖇️ **Source code**: [https://github.com/brpaz/ansible-role-swarm-grafana-alloy](https://github.com/brpaz/ansible-role-swarm-grafana-alloy)
