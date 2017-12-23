# Jsr223 Addon
This docker image allows one to directly use jython in openhab 2.

# Requirements
- Docker
- Docker-Compose
- See the official Docker-Image for further information: https://hub.docker.com/r/openhab/openhab/

# Installation steps
- `git clone git@github.com:smerschjohann/docker-oh2-jsr223.git`
- `docker-compose build`
- start with `docker-compose up -d`
- look at it with docker-compose logs -f and tail -f run/userdata/logs/openhab.log. It should load up the oh1compat.py after around 20 seconds.
- On first startup of Openhab 2, install the experimental rule engine.

# Oh1 Compatibility layer
The file `0oh1compat.py` can be used to migrate the jsr223 scripts from OH1 to OH2.
The rules can look like this:

```
execfile("/openhab/conf/automation/custom/common/execMap.py")

class AlexaAudio(Rule):
    def __init__(self):
        self.triggers = [CommandEventTrigger("SimonPC"), CommandEventTrigger("SimonTV"), CommandEventTrigger("SimonAlexa")]
        self.mapping = { "SimonPC": "PC", "SimonTV": "TV", "SimonAlexa": "ALEXA" }

    def execute(self, event):
        if event.itemCommand == OnOffType.OFF:
            oh.sendCommand("ReceiverSimonPower", "OFF")
            oh.sendCommand("SimonTVCmd", "PowerOff")
        else:
            it = self.mapping[event.itemName]
            oh.sendCommand("ReceiverSimonChannel", it)
            if event.itemName == "SimonTV":
                oh.sendCommand("SimonTVCmd", "WakeUp")

class IrTransmitter(ExecRule):
    def __init__(self, device, irmap):
        ExecRule.__init__(self, irmap)
        self.device = device

    def commandTriggered(self, command):
        self.log.info("commandTriggered: {}", command)
        callList = ["ssh", "-i", "/openhab/conf/automation/custom/openhab_pi", "openhab@192.168.199.10", "irsend", "SEND_ONCE", self.device, command]
        call(callList)

ohInit(automationManager, [
  AlexaAudio(),
  IrTransmitter("DENON", {
      "ReceiverSimonPowerCmd": { "ON": "ON", "OFF": "OFF" },
      "ReceiverSimonVolumeCmd": { "ON": "VOL+", "OFF": "VOL-" },
      "ReceiverSimonChannel": { "PC": "4", "TV": "5", "ALEXA": "2" }
  })
])
```

Happy coding!
