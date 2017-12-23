from subprocess import call

class ExecRule(Rule):
    def __init__(self, commandMap):
        self.commandMap = commandMap

    def commandTriggered(self, command):
        pass

    def getEventTrigger(self):
        events = []

        for x in self.commandMap.iterkeys():
            events.append(CommandEventTrigger(x, None))

        return events

    def execute(self, event):        
        item_map = self.commandMap[event.itemName]
        triggered = str(event.itemCommand)
        cmd = item_map[triggered]
        self.commandTriggered(cmd)
