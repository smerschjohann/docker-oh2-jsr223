se.importPreset("RuleSupport")
se.importPreset("RuleSimple")
se.importPreset("RuleFactories")

from org.openhab.core.automation.handler import TriggerHandler
import uuid

print se.presets
print dir()

def _buildTrigger(uid, typeUID, config):
    return TriggerBuilder.create().withId(uid).withTypeUID(typeUID).withConfiguration(config).build()

class _StartupTriggerHandlerFactory(TriggerHandlerFactory):
    class Handler(TriggerHandler):
        def __init__(self, trigger):
            self.trigger = trigger

        def setRuleEngineCallback(self, rule_engine_callback):
            rule_engine_callback.triggered(self.trigger, {})

    def get(self, trigger):
        return StartupTriggerHandlerFactory.Handler(trigger)

    def ungetHandler(self, module, ruleUID, handler):
        pass

    def dispose(self):
        pass

STARTUP_MODULE_ID = "jsr223.StartupTrigger"
automationManager.addTriggerType(TriggerType(STARTUP_MODULE_ID, [], []))
automationManager.addTriggerHandler(STARTUP_MODULE_ID, _StartupTriggerHandlerFactory())


def StartupTrigger(triggerName=None):
    triggerName = triggerName or uuid.uuid1().hex
    return _buildTrigger(triggerName, STARTUP_MODULE_ID, Configuration())


def ChangedEventTrigger(itemName, oldState=None, newState=None, triggername=None):
    if not triggername:
        triggername = itemName

    return _buildTrigger(triggername, "core.ItemStateChangeTrigger", Configuration({
        "itemName": itemName,
        "state": str(newState) if newState else None,
        "oldState": str(oldState) if oldState else None
    }))

def UpdatedEventTrigger(itemName, state=None, triggername=None):
    if not triggername:
        triggername = itemName

    return _buildTrigger(triggername, "core.ItemStateUpdateTrigger", Configuration({
        "itemName": itemName,
        "state": str(state) if state else None
    }))

def CommandEventTrigger(itemName, command=None, triggername=None):
    if not triggername:
        triggername = itemName

    cfg = {
        "itemName": itemName
    }

    if command:
        cfg["command"] = str(command)

    return _buildTrigger(triggername, "core.ItemCommandTrigger", Configuration(cfg))

def TimerTrigger(expression, triggername=None):
    return _buildTrigger(triggername, "timer.GenericCronTrigger", Configuration({
        "cronExpression": expression
    }))

def stateCondition(itemName, state, condName):
    return Condition(condName, "core.ItemStateCondition", Configuration({
        "itemName": itemName,
        "operator": "=",
        "state": state
    }), {})


import threading
import org.joda.time.DateTime as DateTime
import org.joda.time.Seconds as Seconds

class OpenhabTimer(object):
    def __init__(self, in_seconds, runnable):
        self.runnable = runnable
        self.reschedule(in_seconds)

    def reschedule(self, next_time):
        try:
            seconds = next_time
            if next_time.__class__.__name__ == "DateTime":
                seconds = Seconds.secondsBetween(DateTime.now(), next_time).getSeconds()

            self.timer = threading.Timer(seconds, self.runnable)
            self.timer.start()
        except Exception, e:
            print e

    def cancel(self):
        self.timer.cancel()

from org.slf4j import LoggerFactory
from org.osgi.framework import FrameworkUtil

class osgi(object):
    @staticmethod
    def get_service(class_or_name):
        _bundle = FrameworkUtil.getBundle(type(scriptExtension))
        bundle_context = _bundle.getBundleContext() if _bundle else None
        if bundle_context:
            classname = class_or_name.getName() if isinstance(class_or_name, type) else class_or_name
            ref = bundle_context.getServiceReference(classname)
            return bundle_context.getService(ref) if ref else None

    @staticmethod
    def find_services(class_name, filter):
        _bundle = FrameworkUtil.getBundle(type(scriptExtension))
        bundle_context = _bundle.getBundleContext() if _bundle else None
        if bundle_context:
            refs = bundle_context.getAllServiceReferences(class_name, filter)
            if refs:
                return [bundle_context.getService(ref) for ref in refs]

class oh(object):
    @staticmethod
    def getActions():
        oh1_actions = osgi.find_services("org.openhab.core.scriptengine.action.ActionService", None) or []
        oh2_actions = osgi.find_services("org.eclipse.smarthome.model.script.engine.action.ActionService", None) or []

        return oh1_actions + oh2_actions

    @staticmethod
    def getAction(actionName):
        for action in oh.getActions():
            if actionName in action.__class__.__name__:
                return action.actionClass
        return None

    @staticmethod
    def getState(itemName):
        return unicode(ir.getItem(itemName).state)

    @staticmethod
    def sendCommand(itemName, cmd):
        item = itemName
        if isinstance(itemName, basestring):
            item = ir.getItem(itemName)

        if not isinstance(cmd, basestring):
            cmd = str(cmd)

        print "sendCommand", item, cmd

        events.sendCommand(item, cmd)

    @staticmethod
    def postUpdate(itemName, state):
        item = itemName
        if isinstance(itemName, basestring):
            item = ir.getItem(itemName)

        if not isinstance(state, basestring):
            state = unicode(state)

        events.postUpdate(item, state)

    @staticmethod
    def createTimer(time, runnable):
        return OpenhabTimer(time, runnable)

    @staticmethod
    def getLogger(logName):
        return LoggerFactory.getLogger("org.eclipse.smarthome.automation.rules."+logName)

from collections import defaultdict
class Event(defaultdict):
    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, name):
        return self[name]

import traceback
class Oh1Rule(SimpleRule):
    def __init__(self, rule):
        try:
            self.name = rule.name
        except:
            pass

        if not self.name:
            self.name = type(rule).__name__

        self.triggers = []
        try:
            self.triggers.extend(rule.triggers)
        except:
            pass

        self.conditions = []
        try:
            self.conditions.extend(rule.conditions)
        except:
            pass

        self.log = LoggerFactory.getLogger("org.eclipse.smarthome.automation.rules."+self.name)
        self.rule = rule
        self.rule.log = self.log
        try:
            self.triggers.extend(rule.getEventTriggers())
            self.conditions.extend(rule.getConditions())
        except Exception, ex:
            pass

    def execute(self, module, inputs):
        try:
            self.rule.module = module
            self.rule.inputs = inputs
            self.rule.execute(inputs.get("event"))
        except Exception, ex:
            self.log.error("could not execute: {}", traceback.format_exc())


class EmptyRule(object):
    log = LoggerFactory.getLogger("org.eclipse.smarthome.automation.rules.EmptyRule")

def oh1Rule(rule):
    return Oh1Rule(rule)

def ohInit(hr, rules):
    for rule in rules:
        try:
            pyRule = oh1Rule(rule)
            addedRule = hr.addRule(pyRule)
            LoggerFactory.getLogger("org.eclipse.smarthome.automation.rules.OHINIT").info("new rule: {}", pyRule.name)

            try:
                rule.uid = addedRule.uid
            except:
                pass

        except Exception, ex:
            LoggerFactory.getLogger("org.eclipse.smarthome.automation.rules.OHINIT").error("error adding {}", ex)

import org.openhab.core.automation.module.script.ScriptExtensionProvider as ScriptExtensionProvider

class Oh1Compat(ScriptExtensionProvider):
    def getDefaultPresets(self):
        return ["RuleSupport", "oh"]

    def getPresets(self):
        return ["oh"]

    def getTypes(self):
        return []

    def get(self, scriptEngineId, importType):
        return None

    def importPreset(self, scriptEngineId, preset):
        return {
            "oh": oh,
            "Rule": EmptyRule,
            "ohRule": oh1Rule,
            "ohInit": ohInit,
            "ChangedEventTrigger": ChangedEventTrigger,
            "UpdatedEventTrigger": UpdatedEventTrigger,
            "CommandEventTrigger": CommandEventTrigger,
            "TimerTrigger": TimerTrigger,
            "StartupTrigger": StartupTrigger
        }

    def unload(self, scriptEngineId):
        return

oh1compat = Oh1Compat()

def scriptLoaded(id):
    se.addScriptExtensionProvider(oh1compat)

def scriptUnloaded():
    se.removeScriptExtensionProvider(oh1compat)

