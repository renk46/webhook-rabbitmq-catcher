# General
A docker container that has a django application on board that collects a webhook and puts it in RabbitMQ

## How to use
`docker compose up -d`

## Last Update
Added proxy mode - the message is sent to another host (For example, in a local network behind NAT). If the message does not reach the endpoint, save it in rabbitMQ. Settings in docker-compose.yaml:

```yaml
- PROXY_MODE=1 # Enable proxy mode
- PROXY_ENDPOINT=http://localhost:8080/webhook # Endpoint proxy mode
```
