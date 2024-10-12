# mumble-watcher

Bot that watches a Mumble server and notifies a Telegram group when someone joins/leaves

## Prerequisites

* `pacman -S libolm`
* `slice2py /usr/share/mumble-server/MumbleServer.ice` to generate Python ZeroC Ice bindings
* `pip -r requirements.txt`

## Configuring

* Invite the bot account to the room (you have to accept the invite manually)
* Run `matrix_login.py` once to generate config file
* Add the following section to `config.json`'s dict:
```json
{
    "mumble": {
        "ice_secret": "YOUR_ICE_SECRET"
    }
}
```

## Running

* `main.py` -- run bot
* `mumble-watcher.service` is a systemd unit that starts `main.py`
