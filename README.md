# mumble-watcher

Bot that watches a Mumble server and notifies a Telegram group when someone joins/leaves

## Prerequisites

* `cp /usr/share/mumble-server/MumbleServer.ice .`
* `docker build .`

## Configuring

* Invite the bot account to the room (you have to accept the invite manually)
* Copy `config.example.json` to `config.json`, edit as necessary
* Run `docker run --rm -it -v $(pwd):/cfg mumble-watcher login` once to login into Matrix

## Running

### Docker Compose

Sample `docker-compose.yaml`:

```yaml
services:
  mumble-watcher:
    image: mumble-watcher
    build: /opt/mumble-watcher
    container_name: mumble-watcher
    volumes:
      - /opt/mumble-watcher/config.json:/cfg/config.json
    restart: unless-stopped
    networks:
      mumble-watcher_net:
        ipv4_address: 172.16.0.1

networks:
  mumble-watcher_net:
    ipam:
      config:
        - subnet: 172.16.0.0/31
          gateway: 172.16.0.0
    driver_opts:
      com.docker.network.bridge.name: br-mumble-watch
```
