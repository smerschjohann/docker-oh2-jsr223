class CountdownTimer(Rule):
    def __init__(self, timerItem, timerCurrent, timerDuration, commandItem):
        self.timer = None
        self.timerItem = timerItem
        self.timerCurrent = timerCurrent
        self.timerDuration = timerDuration
        self.commandItem = commandItem

    def getEventTrigger(self):
        return [
            CommandEventTrigger(self.timerItem, None)
        ]

    def timerEval(self):
        timerCurrent = ir.getItem(self.timerCurrent)
        remaining = timerCurrent.state.intValue() - 1

        if remaining > 0:
            oh.postUpdate(self.timerCurrent, str(remaining))
            self.timer.reschedule(DateTime.now().plusMinutes(1))
        else:
            oh.sendCommand(self.commandItem, "OFF")
            oh.postUpdate(self.timerItem, "OFF")
            self.timer = None

    def execute(self, event):
        self.log.info("timer {} => {}", event.itemName, event.itemCommand)
        if str(event.itemCommand) == "ON":
            timerDuration = ir.getItem(self.timerDuration)
            self.log.info("timer activated duration={}", str(timerDuration.state))
            oh.postUpdate(self.timerCurrent, str(timerDuration.state))
            if self.timer:
                self.timer.cancel()
            self.timer = oh.createTimer(DateTime.now().plusMinutes(1), self.timerEval)

        else:
            if self.timer:
                self.timer.cancel()
                self.timer = None
