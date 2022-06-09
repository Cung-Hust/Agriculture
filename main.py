import codecs
import json
import os
from time import sleep
from pathlib import Path
import sys
from datetime import datetime

from PyQt5.QtGui import QGuiApplication, QIcon
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QObject, QTimer, QThread, QSettings, QCoreApplication
import random
import sqlite3
import GPIOPI
import PackData
import paho.mqtt.client as mqtt
import serial
import struct
import hashlib
import logging
from logging.handlers import TimedRotatingFileHandler

d = os.path.dirname(__file__)

mac = open("/sys/firmware/devicetree/base/serial-number").read()
mac_add = mac[0:16]
loghandler = TimedRotatingFileHandler(
    filename=d + f"{mac_add}.txt", when="MIDNIGHT", backupCount=5
)
logfomatter = logging.Formatter(fmt=("%(asctime)s\t" "%(levelname)s\t" "%(message)s"))
logger = logging.getLogger("mylog")
loghandler.setFormatter(logfomatter)
logger.addHandler(loghandler)
logger.propagate = False
logger.setLevel(logging.DEBUG)


sql = None
client = mqtt.Client()
ble = mqtt.Client()
clientOTA = mqtt.Client()
ListPort = json.load(open("ConfigurePort.json"))
IP_SERVER = ListPort["Server"]["IP"]
PORT_SERVER = ListPort["Server"]["Port"]
PORT_BLE = ListPort["BLE"]["Port"]
PORT_GW = ListPort["Gateway"]["Port"]
BAUD_GW = ListPort["Gateway"]["Baud"]
USER_SERVER = ListPort["Server"]["User"]
PASS_SERVER = ListPort["Server"]["Pass"]


class ScanLoraGateway(QThread):
    """
    Scan Lora message
    """

    def run(self):
        while True:
            gatewayMessage.getCommandLora()


class ScanReconnectMQTT(QThread):
    """
    Scan Connect MQTT
    """

    def run(self):
        connect = engine.rootObjects()[0].findChild(QObject, "connection")
        number_dis = 0
        while True:
            flag = os.system("ping -c 4 " + IP_SERVER)
            # flag = os.system("ping " + IP_SERVER)
            if flag == 0:
                connect.setProperty("connected", True)
                number_dis = 0
            else:
                connect.setProperty("connected", False)
                if number_dis == 60:
                    os.system("sudo reboot")
                number_dis += 1
            sleep(10)


class SQL:
    """
    SQL class
    """

    def __init__(self):
        self.db = sqlite3.connect("gateway1.db")

    """
        BLE Device
    """

    def insertDeviceBLE(self, group, unicast):
        cmd = "INSERT INTO deviceBLE (groupDevice, unicast) VALUES (?,?)"
        cursor = self.db.cursor()
        cursor.execute(cmd, [group, unicast])
        self.db.commit()

    def getDeviceBLE(self, group):
        cmd = "SELECT * FROM deviceBLE WHERE groupDevice=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [group])
        return cursor.fetchall()

    def deleteDeviceBLE(self, group):
        cmd = "DELETE FROM deviceBLE WHERE groupDevice=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [group])
        self.db.commit()

    """
        Gateway Command SQL
    """

    def insertGatewayCommand(self, uni, active):
        cmd = "INSERT INTO gateway (uni, active) VALUES (?,?)"
        cursor = self.db.cursor()
        cursor.execute(cmd, [uni, active])
        self.db.commit()

    def deleteGatewayCommand(self, uni):
        cmd = "DELETE FROM gateway WHERE uni=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [uni])
        self.db.commit()

    def getGatewayCommand(self, uni):
        cmd = "SELECT * FROM gateway WHERE uni=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [uni])
        return cursor.fetchall()

    """
        Cloud Command SQL
    """

    def insertCommandCloud(self, mess):
        cmd = "INSERT INTO cloud (message)" " VALUES (?)"
        value = [mess]
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        print(cmd, mess)
        self.db.commit()

    def deleteCommandCloud(self):
        cmd = "DELETE FROM cloud"
        cursor = self.db.cursor()
        cursor.execute(cmd)
        self.db.commit()

    def getCommandCloud(self):
        cmd = "SELECT * FROM cloud"
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    """
        Get Script from SQL
    """

    def getMultiScript(self):
        cmd = "SELECT * FROM script"
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getSingleScript(self, id):
        cmd = "SELECT * FROM script WHERE id=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [id])
        return cursor.fetchall()

    def getConditionScript(self, idScript):
        cmd = "SELECT * FROM conditionscript WHERE script=" + str(idScript)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getActionScript(self, idScript):
        cmd = "SELECT * FROM actionscript WHERE script=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [idScript])
        return cursor.fetchall()

    def updateConditionScript(self, idScript):
        """
        :param idScript: id of Script
        :return:
        """
        timeNow = datetime.now()
        timeStart = timeNow.hour * 3600 + timeNow.minute * 60 + timeNow.second
        stop = 0
        allAction = self.getActionScript(idScript)
        for singleAction in allAction:
            idAction = singleAction[0]
            self.updateRunActionScript(status=1, idAction=idAction)
            delay = singleAction[6]
            during = singleAction[7]
            if delay + during > stop:
                stop = delay + during
        cmd = "UPDATE conditionscript SET start=?, stop=? WHERE script=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [timeStart, timeStart + stop * 60, idScript])
        self.db.commit()

    def updateRunActionScript(self, status, idAction):
        """
        :param status:
        :param idAction:
        :return:
        """
        cmd = "UPDATE actionscript SET run=? WHERE id=?"
        cursor = self.db.cursor()
        print("update Action:", idAction, "status", status)
        logger.info(f"update Action:{idAction} status {status}")
        cursor.execute(cmd, [status, idAction])
        self.db.commit()

    def updateScript(self, value):
        cmd = "UPDATE script SET " "name=? " "WHERE id=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def updateActiveScript(self, active, idScript):
        cmd = "UPDATE script SET active=? WHERE id=?"
        value = [active, idScript]
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def insertActionScript(self, value):
        cmd = (
            "INSERT INTO actionscript (script, device, status, dim, cct, delay, during, run)"
            " VALUES (?,?, ?, ?, ?, ?, ?, ?)"
        )
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def insertConditionScript(self, value):
        cmd = "INSERT INTO conditionscript (script,start, stop)" " VALUES (?, ?, ?)"
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def insertScript(self, value):
        cmd = "INSERT INTO script " "(id,name,active) VALUES (?,?,?)"
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def deleteActionScript(self, idScript):
        cmd = "DELETE FROM actionscript WHERE script=" + str(idScript)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        self.db.commit()

    def deleteScript(self, idScript):
        cmd = "DELETE FROM script WHERE id=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [idScript])
        self.deleteConditionScript(idScript)
        self.deleteActionScript(idScript)
        self.db.commit()

    def deleteConditionScript(self, idScript):
        cmd = "DELETE FROM conditionscript WHERE script=" + str(idScript)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        self.db.commit()

    def deleteActionIsScript(self, idScript):
        cmd = "DELETE FROM actionrules WHERE device=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [idScript])
        self.db.commit()

    """
        Device (Relay or Led) SQl
    """

    def getMultiDevice(self):
        cmd = "SELECT * FROM device"
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getSingleDeviceAtID(self, id):
        cmd = "SELECT * FROM device WHERE id=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [id])
        return cursor.fetchall()

    def getSingleDeviceAtMac(self, mac):
        cmd = "SELECT * FROM device WHERE mac=" + mac
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def deleteDeviceAtMac(self, mac):
        cmd = "DELETE FROM device WHERE mac=" + mac
        cursor = self.db.cursor()
        cursor.execute(cmd)
        self.db.commit()

    def deleteActionDevice(self, idDevice):
        cursor = self.db.cursor()
        cmd = "DELETE FROM actiontimeline WHERE device=" + str(idDevice)
        cursor.execute(cmd)
        cmd = "DELETE FROM actionrules WHERE device=" + str(idDevice)
        cursor.execute(cmd)
        cmd = "DELETE FROM actionscript WHERE device=" + str(idDevice)
        cursor.execute(cmd)
        self.db.commit()

    def insertDevice(self, value):
        command = (
            "INSERT INTO device ( "
            "name, "
            "mac, "
            "uni,"
            "isExtend, "
            "isRelay, "
            "pin,"
            "status , "
            "dim,"
            "cct"
            ")"
            " VALUES (?, ?,?,?,?, ?, ?,?,?)"
        )
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def updateDevice(self, value):
        command = "UPDATE device SET " "name= ?, " "pin=?" "WHERE id=?"
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def updateNameDevice(self, name, pin, id):
        command = "UPDATE device SET " "name= ? ," "pin=? " "WHERE id=?"
        cursor = self.db.cursor()
        cursor.execute(command, [name, pin, id])
        self.db.commit()

    def updateStatusDevice(self, status, id):
        value = [status, id]
        command = "UPDATE device SET " "status= ? " "WHERE id=?"
        cursor = self.db.cursor()
        print(command, value)
        cursor.execute(command, value)
        self.db.commit()

    def updateDimDevice(self, dim, id):
        value = [dim, id]
        command = "UPDATE device SET " "dim= ? " "WHERE id=?"
        cursor = self.db.cursor()
        print(command, value)
        cursor.execute(command, value)
        self.db.commit()

    def updateCCTDevice(self, cct, id):
        value = [cct, id]
        command = "UPDATE device SET " "cct= ? " "WHERE id=?"
        cursor = self.db.cursor()
        print(command, value)
        cursor.execute(command, value)
        self.db.commit()

    """
        Sensor SQL
    """

    def getMultiSensor(self):
        cmd = "SELECT * FROM sensor"
        cursor = self.db.cursor()

        cursor.execute(cmd)
        return cursor.fetchall()

    def getSingleSensorAtID(self, idSensor):
        cmd = "SELECT * FROM sensor WHERE id=" + str(idSensor)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getSingleSensorAtMac(self, mac):
        cmd = "SELECT * FROM sensor WHERE mac=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [mac])
        return cursor.fetchall()

    def getSingleSensorAtHash(self, hash):
        cmd = "SELECT * FROM sensor WHERE hashMac=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [hash])
        return cursor.fetchall()

    def getSingleSensorAtHashType(self, hash, type):
        cmd = "SELECT * FROM sensor WHERE hashMac=? and type=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [hash, type])
        return cursor.fetchall()

    def getSingleSensorAtUni(self, uni):
        cmd = "SELECT * FROM sensor WHERE uni=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [uni])
        return cursor.fetchall()

    def deleteSensorAtMac(self, mac):
        cmd = "DELETE FROM sensor WHERE mac=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [mac])
        self.db.commit()

    def deleteConditionSensor(self, idSensor):
        cursor = self.db.cursor()
        cmd = "DELETE FROM conditionrules WHERE sensor=" + str(idSensor)
        cursor.execute(cmd)
        self.db.commit()

    def insertSensor(self, value):
        command = (
            "INSERT INTO sensor ( "
            "name, "
            "mac,"
            "uni,"
            "type , "
            "value , "
            "pin, "
            "minValue, "
            "maxValue, "
            "par_a, "
            "par_b, "
            "par_c, "
            "delay ,"
            "hashMac"
            ")"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?, ?,?)"
        )
        cursor = self.db.cursor()

        cursor.execute(command, value)
        self.db.commit()

    def updateNameSensor(self, value):
        command = "UPDATE sensor SET " "name= ? " "WHERE hashMac=? AND type=?"
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def updateCalibSensor(self, value):
        command = (
            "UPDATE sensor SET "
            "minValue=?,"
            "maxValue = ?,"
            "par_a = ?, "
            "par_b = ?, "
            "par_c = ?, "
            "delay = ? "
            "WHERE hashMac=? AND type=?"
        )
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def updateDelaySensor(self, value):
        command = "UPDATE sensor SET " "delay = ? " "WHERE hashMac=?"
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def updateValueSensor(self, value, uni):
        value = [value, uni]
        command = "UPDATE sensor SET " "value= ? " "WHERE uni=?"
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def updateValueSensorAtType(self, value, uni, type):
        value = [value, uni, type]
        command = "UPDATE sensor SET " "value= ? " "WHERE uni=? AND type=?"
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def updateBatterySensor(self, value, uni):
        value = [value, uni]
        command = "UPDATE sensor SET " "pin=? " "WHERE uni=?"
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    """
        Rules from SQL
    """

    def getMultiRulesSql(
        self,
    ):
        cmd = "SELECT * FROM rules"
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getSingleRulesSql(self, id):
        cmd = "SELECT * FROM rules WHERE id=" + str(id)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getConditionRules(self, idRules):
        cmd = "SELECT * FROM conditionrules WHERE rules=" + str(idRules)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getConditionRules2(self, idRules):
        cmd = "SELECT * FROM conditionrules2 WHERE rules=" + str(idRules)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getConditionRules3(self, idRules):
        cmd = "SELECT * FROM conditionrules3 WHERE rules=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [idRules])
        return cursor.fetchall()[0]

    def getActionRules(self, id):
        cmd = "SELECT * FROM actionrules WHERE rules=" + str(id)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def insertRulesSql(self, value):
        command = "INSERT INTO rules ( " "id, name,active)" " VALUES (?,?,?)"
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def insertConditionRules(self, value):
        cmd = "INSERT INTO conditionrules (rules, sensor, compare, value) VALUES (?, ?, ?, ?)"
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def insertConditionRules2(self, value):
        cmd = (
            "INSERT INTO conditionrules2 (rules, timeStart, timeStop, timeUpdate, t2, t3, t4, t5, t6, t7, t8, logic)"
            " VALUES (?, ?, ?, ?,?, ?, ?, ?,?, ?, ?, ?)"
        )
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def insertConditionRules3(self, value):
        cmd = (
            "INSERT INTO conditionrules3 (rules, start, stop, run)"
            " VALUES (?, ?, ?, ?)"
        )
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def insertActionRules(self, value):
        cmd = (
            "INSERT INTO actionrules "
            "(rules, isDevice, device, status, dim, cct, delay, during)"
            " VALUES (?,?,?,?,?,?,?,?)"
        )
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def updateRulesSql(self, value):
        command = "UPDATE rules SET " "name= ?" " WHERE id=?"
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def updateActiveRulesSql(self, idScript, active):
        command = "UPDATE rules SET " "active=? " "WHERE id=?"
        cursor = self.db.cursor()
        value = [active, idScript]
        cursor.execute(command, value)
        self.db.commit()

    def updateConditionRules3(self, run, idRules):
        """
        :param run:
        :param idRules:
        :return: None
        """
        datetimeNow = datetime.now()
        timeNow = datetimeNow.hour * 3600 + datetimeNow.minute * 60
        maxTime = 0
        if run == 1:
            action = self.getActionRules(idRules)
            if len(action) > 0:
                print(f"Action Rules: {action}")
                logger.info(f"Action Rules: {action}")
                if action[0][2] == 1:
                    for singleAction in action:
                        timeAction = singleAction[7] * 60 + singleAction[8] * 60
                        if maxTime < timeAction:
                            maxTime = timeAction
                else:
                    maxTimeScript = 0
                    for singleAction in action:
                        idScript = singleAction[3]
                        actionScript = self.getActionScript(idScript=idScript)
                        for singleDevice in actionScript:
                            timeAction = singleDevice[7] * 60 + singleDevice[8] * 60
                            if maxTimeScript < timeAction:
                                maxTimeScript = timeAction
                        if maxTime < maxTimeScript:
                            maxTime = maxTimeScript
            else:
                self.deleteConditionRules(idRules)
                self.deleteConditionRules2(idRules)
                self.deleteConditionRules3(idRules)
                self.deleteRulesSql(idRules)

        cmd = "UPDATE conditionrules3 " "SET start=?, stop=? , run=?" " WHERE rules=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [timeNow, timeNow + maxTime, run, idRules])
        self.db.commit()

    def deleteRulesSql(self, idRules):
        cmd = "DELETE FROM rules WHERE id=" + str(idRules)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        self.db.commit()

    def deleteConditionRules(self, idRules):
        cmd = "DELETE FROM conditionrules WHERE rules=" + str(idRules)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        self.db.commit()

    def deleteConditionRules2(self, idRules):
        cmd = "DELETE FROM conditionrules2 WHERE rules=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [idRules])
        self.db.commit()

    def deleteConditionRules3(self, idRules):
        cmd = "DELETE FROM conditionrules3 WHERE rules=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [idRules])
        self.db.commit()

    def deleteActionRules(self, idRules):
        cmd = "DELETE FROM actionrules WHERE rules=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, [idRules])
        self.db.commit()

    """ 
        Timeline SQL
    """

    def getMultiTimelineSql(self):
        """
            Get time line of device 1
        :return: form timeline of device 1
        """
        cmd = "SELECT * FROM timeline"
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getSingleTimelineSql(self, id):
        cmd = "SELECT * FROM timeline WHERE id=" + str(id)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getActionTimeline(self, idTimeline):
        cmd = "SELECT * FROM actiontimeline WHERE timeline=" + str(idTimeline)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def getConditionTimeline(self, idTimeline):
        cmd = "SELECT * FROM conditiontimeline WHERE timeline=" + str(idTimeline)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def insertTimelineSql(self, value):
        cmd = "INSERT INTO timeline ( id, name,active) " "VALUES (?,?,?)"
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def insertConditionTimeline(self, value):
        cmd = (
            "INSERT INTO conditiontimeline (timeline, time, t2, t3, t4, t5, t6, t7, t8)"
            " VALUES (?,?,?,?,?,?,?,?,?)"
        )
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def insertActionTimeline(self, value):
        cmd = (
            "INSERT INTO actiontimeline (timeline, device, status, dim, cct)"
            " VALUES (?,?,?,?,?)"
        )
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def updateActiveTimelineSql(self, active, id):
        cmd = "UPDATE timeline SET active=? WHERE id=?"
        value = [active, id]
        cursor = self.db.cursor()

        cursor.execute(cmd, value)
        self.db.commit()

    def updateTimelineSql(self, value):
        """
            Set time line of device 1
        :return: None
        """
        command = "UPDATE timeline SET name= ? WHERE id=?"
        cursor = self.db.cursor()
        cursor.execute(command, value)
        self.db.commit()

    def updateConditionTimeline(self, value):
        cmd = (
            "UPDATE conditiontimeline SET"
            " timeline=?, time=?, t2=?, t3=?, t4=?, t5=?, t6=?, t7=?, t8=? WHERE id=?"
        )
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def updateActionTimeline(self, value):
        cmd = "UPDATE actiontimeline SET" " status=?, dim=?, cct=? WHERE id=?"
        cursor = self.db.cursor()
        cursor.execute(cmd, value)
        self.db.commit()

    def deleteTimelineSql(self, id):
        cmd = "DELETE FROM timeline WHERE id=" + str(id)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        self.db.commit()

    def deleteActionTimeline(self, idTimeline):
        cmd = "DELETE FROM actiontimeline WHERE timeline=" + str(idTimeline)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        self.db.commit()

    def deleteConditionTimeline(self, idTimeline):
        cmd = "DELETE FROM conditiontimeline WHERE timeline=" + str(idTimeline)
        cursor = self.db.cursor()
        cursor.execute(cmd)
        self.db.commit()


class Timeline:
    """
    Class for Timeline Object
    """

    def __init__(self):
        self.timelinePage = engine.rootObjects()[0].findChild(QObject, "timelinePage")
        self.timelinePage.seach.connect(lambda: self._seachNewTimeline())

    def showSingleTimeline(self, valueTimeline):
        """
        :param valueTimeline:
        """
        idTimeline = valueTimeline[0]
        if self.timelinePage.property("newTimeline") is True:
            self.timelinePage.addTimeline(idTimeline)
            objecTimeline = engine.rootObjects()[0].findChild(
                QObject, "timeline" + str(idTimeline)
            )
            objecTimeline.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteTimeline()
            )
            objecTimeline.findChild(QObject, "active").clicked.connect(
                lambda: self.updateActiveTimeline(action=0)
            )
            self.timelinePage.setProperty("newTimeline", False)
        objecTimeline = engine.rootObjects()[0].findChild(
            QObject, "timeline" + str(idTimeline)
        )
        objecTimeline.setProperty("nameAction", valueTimeline[1])
        objecTimeline.setProperty("activeAction", valueTimeline[2])

    def updateActiveTimeline(self, active=None, idTimeline=None, action=None):
        """
        :param active:
        :param idTimeline: ID of Timeline
        :param action: 0 from gateway, 1 from server
        :return: None
        """
        if action == 0:
            idTimeline = self.timelinePage.property("currentTimeline")
            active = self.timelinePage.property("currentActive")
        else:
            engine.rootObjects()[0].findChild(
                QObject, "timeline" + str(idTimeline)
            ).setProperty("activeAction", active)
        SQL().updateActiveTimelineSql(active, idTimeline)
        if action == 0:
            objectTimeline = sql.getSingleTimelineSql(idTimeline)[0]
            packageTimeline = PackData.PackRule(
                id=objectTimeline[0],
                type=PackData.TypeRule["Schedule"],
                active=objectTimeline[2],
                action=PackData.TypeAction["Update"],
            )
            cloudMessage.sendMessageMqtt([packageTimeline], PackData.FormData["Rule"])

    def showAllTimeline(self):
        """
        :return:
        """
        allTimeline = SQL().getMultiTimelineSql()
        for singleTimeline in allTimeline:
            idTimeline = singleTimeline[0]
            self.timelinePage.addTimeline(idTimeline)
            self.showSingleTimeline(singleTimeline)
            timelineObject = engine.rootObjects()[0].findChild(
                QObject, "timeline" + str(idTimeline)
            )
            timelineObject.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteTimeline()
            )
            timelineObject.findChild(QObject, "active").clicked.connect(
                lambda: self.updateActiveTimeline(action=0)
            )

    def _seachNewTimeline(self):
        allTimeline = sql.getMultiTimelineSql()
        for singleTimeline in allTimeline:
            idTimeline = singleTimeline[0]
            if (
                engine.rootObjects()[0].findChild(QObject, "timeline" + str(idTimeline))
                is None
            ):
                self.timelinePage.setProperty("newTimeline", True)
                self.showSingleTimeline(singleTimeline)

    def deleteTimeline(self, idTimeline=None):
        """
        :param idTimeline:
        :return:
        """
        if idTimeline is None:
            idTimeline = self.timelinePage.property("currentTimeline")
            packageTimeline = PackData.PackRule(
                id=idTimeline,
                type=PackData.TypeRule["Schedule"],
                action=PackData.TypeAction["Delete"],
            )
            cloudMessage.sendMessageMqtt([packageTimeline], PackData.FormData["Rule"])
        else:
            engine.rootObjects()[0].findChild(
                QObject, "timeline" + str(idTimeline)
            ).deleteItem.emit()
        SQL().deleteConditionTimeline(idTimeline)
        SQL().deleteActionTimeline(idTimeline)
        SQL().deleteTimelineSql(idTimeline)


class Rules:
    """
    Class for Rule Object
    """

    def __init__(self):
        self.rulesPage = engine.rootObjects()[0].findChild(QObject, "rulesPage")
        self.rulesPage.seach.connect(lambda: self._seachRules())

    def showAllRules(self):
        allRules = sql.getMultiRulesSql()
        for singleRules in allRules:
            idRules = singleRules[0]
            self.rulesPage.addRules(idRules)
            self.showSingleRules(singleRules)
            rules = self.rulesPage.findChild(QObject, "rules" + str(idRules))
            rules.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteRules()
            )
            rules.findChild(QObject, "active").clicked.connect(
                lambda: self.updateActiveRules()
            )

    def showSingleRules(self, valueRules):
        idRules = valueRules[0]
        if self.rulesPage.property("newRules") is True:
            self.rulesPage.addRules(idRules)
            rules = self.rulesPage.findChild(QObject, "rules" + str(idRules))
            rules.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteRules()
            )
            rules.findChild(QObject, "active").clicked.connect(
                lambda: self.updateActiveRules()
            )
            self.rulesPage.setProperty("newRules", False)
        rules = self.rulesPage.findChild(QObject, "rules" + str(idRules))
        rules.setProperty("idAction", idRules)
        rules.setProperty("nameAction", valueRules[1])
        rules.setProperty("activeAction", valueRules[2])

    def _seachRules(self):
        allRules = sql.getMultiRulesSql()
        for singleRules in allRules:
            idRules = singleRules[0]
            if self.rulesPage.findChild(QObject, "rules" + str(idRules)) is None:
                self.rulesPage.setProperty("newRules", True)
                self.showSingleRules(singleRules)

    def updateActiveRules(self, idRules=None, status=None):
        if status is None:
            idRules = self.rulesPage.property("currentRules")
            activeRules = self.rulesPage.property("activeRules")
            SQL().updateActiveRulesSql(idRules, activeRules)
            objectRule = SQL().getSingleRulesSql(idRules)[0]
            active = objectRule[2]
            packageRule = PackData.PackRule(
                id=idRules,
                type=PackData.TypeRule["Rule"],
                action=PackData.TypeAction["Update"],
                active=active,
            )
            cloudMessage.sendMessageMqtt([packageRule], PackData.FormData["Rule"])
        else:
            engine.rootObjects()[0].findChild(
                QObject, "rules" + str(idRules)
            ).setProperty("activeAction", status)
            SQL().updateActiveRulesSql(idRules, status)

    def deleteRules(self, idRules=None):
        if idRules is None:
            idRules = self.rulesPage.property("currentRules")
            packageRule = PackData.PackRule(
                id=idRules,
                type=PackData.TypeRule["Rule"],
                action=PackData.TypeAction["Delete"],
            )
            cloudMessage.sendMessageMqtt([packageRule], PackData.FormData["Rule"])
        else:
            self.rulesPage.findChild(QObject, "rules" + str(idRules)).deleteItem.emit()
        SQL().deleteRulesSql(idRules)
        SQL().deleteConditionRules(idRules)
        SQL().deleteConditionRules2(idRules)
        SQL().deleteConditionRules3(idRules)
        SQL().deleteActionRules(idRules)


class Script:
    """
    Class for Script Object
    """

    def __init__(self):
        self.scriptPage = engine.rootObjects()[0].findChild(QObject, "scriptPage")
        self.scriptPage.seach.connect(lambda: self._seachScript())

    def showScript(self, value):
        idScript = value[0]
        if self.scriptPage.property("newScript") is True:
            self.scriptPage.addScript(idScript)
            script = self.scriptPage.findChild(QObject, "script" + str(idScript))
            script.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteScript()
            )
            script.findChild(QObject, "active").clicked.connect(
                lambda: self.updateActiveScript(action=0)
            )
            self.scriptPage.setProperty("newScript", False)
        script = self.scriptPage.findChild(QObject, "script" + str(idScript))
        script.setProperty("idAction", idScript)
        script.setProperty("nameAction", value[1])

    def showAllScript(self):
        allScript = sql.getMultiScript()
        for singleScript in allScript:
            idScript = singleScript[0]
            self.scriptPage.addScript(idScript)
            self.showScript(singleScript)
            script = self.scriptPage.findChild(QObject, "script" + str(idScript))
            script.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteScript()
            )
            script.findChild(QObject, "active").clicked.connect(
                lambda: self.updateActiveScript(action=0)
            )

    def _seachScript(self):
        allScript = sql.getMultiScript()
        for singleScript in allScript:
            idScript = singleScript[0]
            if (
                engine.rootObjects()[0].findChild(QObject, "script" + str(idScript))
                is None
            ):
                self.scriptPage.setProperty("newScript", True)
                self.showScript(singleScript)

    def deleteScript(self, idScript=None):
        """
        :param idScript:
        :return:
        """
        if idScript is None:
            idScript = self.scriptPage.property("currentScript")
            packageScript = PackData.PackRule(
                id=idScript,
                type=PackData.TypeRule["Script"],
                action=PackData.TypeAction["Delete"],
            )
            cloudMessage.sendMessageMqtt([packageScript], PackData.FormData["Rule"])
        else:
            self.scriptPage.findChild(
                QObject, "script" + str(idScript)
            ).deleteItem.emit()
        SQL().deleteScript(idScript=idScript)
        SQL().deleteConditionScript(idScript=idScript)
        SQL().deleteActionScript(idScript=idScript)
        SQL().deleteActionIsScript(idScript=idScript)

    def updateActiveScript(self, idScript=None, active=None, action=None):
        """
        :param idScript: ID of Script
        :param active: status of Script
        :param action: 0 is from gateway, 1 is from server, 2 is from rule
        :return: None
        """
        print("UPdate Script 1")
        if action == 0:
            print("UPdate Script 1")
            idScript = self.scriptPage.property("currentScript")
            active = self.scriptPage.findChild(
                QObject, "script" + str(idScript)
            ).property("activeAction")
            SQL().updateConditionScript(idScript)
        else:
            if active == 1:
                status = True
            else:
                status = False
            self.scriptPage.findChild(QObject, "script" + str(idScript)).setProperty(
                "activeAction", status
            )
        SQL().updateActiveScript(active, idScript)
        if action != 1:
            objectScript = SQL().getSingleScript(idScript)[0]
            packageScript = PackData.PackRule(
                id=idScript,
                type=PackData.TypeRule["Script"],
                action=PackData.TypeAction["Update"],
                active=objectScript[2],
            )
            cloudMessage.sendMessageMqtt([packageScript], PackData.FormData["Rule"])
        if active == 0:
            return
        SQL().updateConditionScript(idScript)


class Device:
    """
    Class for Device Control
    """

    def __init__(self):
        self.devicePage = engine.rootObjects()[0].findChild(QObject, "devicePage")
        self.devicePage.seach.connect(lambda: self.seachDevice())

    def showDevice(self, value):
        idDevice = value[0]
        isExtend = value[4]
        isRelay = value[5]
        pinDevice = value[6]
        if self.devicePage.property("newDevice") is True:
            self.devicePage.addDevice(idDevice)
            device = engine.rootObjects()[0].findChild(
                QObject, "device" + str(idDevice)
            )
            if isRelay == 0:
                device.findChild(QObject, "DIM").pressedChanged.connect(
                    lambda: self.updateDimDevice(action=0)
                )
                device.findChild(QObject, "CCT").pressedChanged.connect(
                    lambda: self.updateCCTDevice(action=0)
                )
                device.findChild(QObject, "scanDevice").clicked.connect(
                    lambda: self.scanLedBLE()
                )
            device.findChild(QObject, "active").clicked.connect(
                lambda: self.updateStatusDevice(action=0)
            )
            device.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteDevice()
            )
            self.devicePage.setProperty("newDevice", False)
        device = engine.rootObjects()[0].findChild(QObject, "device" + str(idDevice))
        if isExtend == 1 and isRelay == 1:
            device.setProperty("selectedView", 3)
        if isRelay == 0:
            device.setProperty("selectedView", 4)
        device.setProperty("idDevice", idDevice)
        device.setProperty("activeDevice", value[7])
        device.setProperty("dimDevice", value[8])
        device.setProperty("cctDevice", value[9])
        device.setProperty("nameDevice", value[1])
        device.setProperty("macDevice", value[2])
        if isExtend == 0 and isRelay == 1:
            GPIOPI.setupGPIO(pinDevice, value[7])

    def scanLedBLE(self):
        print("Scan BLE...")
        logger.info("Scan BLE...")
        bleMessage.scanDevice()

    def seachDevice(self):
        allDevice = sql.getMultiDevice()
        for singleDevice in allDevice:
            idDevice = singleDevice[0]
            if self.devicePage.findChild(QObject, "device" + str(idDevice)) is None:
                self.devicePage.setProperty("newDevice", True)
                self.showDevice(singleDevice)

    def showAllDevice(self):
        allDevice = sql.getMultiDevice()
        for singleDevice in allDevice:
            idDevice = singleDevice[0]
            self.devicePage.addDevice(idDevice)
            self.showDevice(singleDevice)
            isRelay = singleDevice[5]
            device = engine.rootObjects()[0].findChild(
                QObject, "device" + str(idDevice)
            )
            if isRelay == 0:
                device.findChild(QObject, "DIM").pressedChanged.connect(
                    lambda: self.updateDimDevice(action=0)
                )
                device.findChild(QObject, "CCT").pressedChanged.connect(
                    lambda: self.updateCCTDevice(action=0)
                )
                device.findChild(QObject, "scanDevice").clicked.connect(
                    lambda: self.scanLedBLE()
                )
            device.findChild(QObject, "active").clicked.connect(
                lambda: self.updateStatusDevice(action=0)
            )
            device.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteDevice()
            )

    def _activeDevice(self, idDevice=None, action=None, type=None):
        """
        :param idDevice: ID of Device
        :param action: 0 or 2 Send command to server
        :param type: 0 is Pull, 1 is Dim, 2 is CCT
        :return:
        """
        singleDevice = SQL().getSingleDeviceAtID(idDevice)[0]
        mac = singleDevice[2]
        isExtend = singleDevice[4]
        isRelay = singleDevice[5]
        pin = singleDevice[6]
        pull = singleDevice[7]
        dim = singleDevice[8]
        cct = singleDevice[9]
        if type != 0 and isRelay == 1:
            return
        unis_group = idDevice + 50000
        if action != 1:
            if type == 0:
                cloudMessage.sendMessageMqtt(
                    [PackData.PackValueControl(id=mac, type=type, pull=pull)],
                    PackData.FormData["Control"],
                )
            elif type == 1:
                cloudMessage.sendMessageMqtt(
                    [
                        PackData.PackValueControl(
                            id=mac, type=PackData.TypeDevice["Led"], dim=dim
                        )
                    ],
                    PackData.FormData["Control"],
                )
            elif type == 2:
                cloudMessage.sendMessageMqtt(
                    [
                        PackData.PackValueControl(
                            id=mac, type=PackData.TypeDevice["Led"], cct=cct
                        )
                    ],
                    PackData.FormData["Control"],
                )
        if type == 0:
            if isRelay == 1 and isExtend == 0:
                GPIOPI.setupGPIO(pin, pull)
            elif isRelay == 0 and isExtend == 0:
                bleMessage.controlONOFF(unis_group, pull)
        elif type == 1:
            bleMessage.controlDIM(unis_group, dim)
        elif type == 2:
            bleMessage.controlCCT(unis_group, cct)

    def updateDimDevice(self, dim=None, idDevice=None, action=None):
        """
        :param dim: Dim of Device
        :param idDevice: ID of Device
        :param action: 0 is from gateway, 1 is from server, 2 is from rule
        :return: None
        """
        if action == 0:
            idDevice = self.devicePage.property("currentDevice")
            device = engine.rootObjects()[0].findChild(
                QObject, "device" + str(idDevice)
            )
            if device.property("pressed1") is False:
                dim = self.devicePage.property("dim")
                dim_old = sql.getSingleDeviceAtID(idDevice)[0][8]
                if dim == dim_old:
                    return
                SQL().updateDimDevice(dim, idDevice)
        elif action == 1 or action == 2:
            SQL().updateDimDevice(dim, idDevice)
            engine.rootObjects()[0].findChild(
                QObject, "device" + str(idDevice)
            ).setProperty("dimDevice", dim)
        self._activeDevice(idDevice=idDevice, action=action, type=1)

    def updateCCTDevice(self, cct=None, idDevice=None, action=None):
        """
        :param cct: CCT of Device
        :param idDevice: ID of Device
        :param action: 0 is from gateway, 1 is from server, 2 is from rule
        :return: None
        """
        if action == 0:
            idDevice = self.devicePage.property("currentDevice")
            device = engine.rootObjects()[0].findChild(
                QObject, "device" + str(idDevice)
            )
            if device.property("pressed2") is False:
                cct = self.devicePage.property("cct")
                cct_old = sql.getSingleDeviceAtID(idDevice)[0][9]
                if cct == cct_old:
                    return
                SQL().updateCCTDevice(cct, idDevice)
        else:
            SQL().updateCCTDevice(cct, idDevice)
            engine.rootObjects()[0].findChild(
                QObject, "device" + str(idDevice)
            ).setProperty("cctDevice", cct)
        self._activeDevice(idDevice=idDevice, action=action, type=2)

    def updateStatusDevice(self, pull=None, idDevice=None, action=None):
        """
        :param pull:
        :param idDevice: is ID of Device
        :param action: 0 is from gateway, 1 is from server, 2 is from rule
        :return: None
        """
        if action == 0:
            pull = self.devicePage.property("activeDevice")
            idDevice = self.devicePage.property("currentDevice")
            SQL().updateStatusDevice(pull, idDevice)
        elif action == 1 or action == 2:
            SQL().updateStatusDevice(pull, idDevice)
            if pull == 1:
                status = True
            else:
                status = False
            self.devicePage.findChild(QObject, "device" + str(idDevice)).setProperty(
                "activeDevice", status
            )
        self._activeDevice(idDevice=idDevice, action=action, type=0)

    def deleteDevice(self, mac=None):
        """
        :param mac:
        """
        if mac is None:
            idDevice = self.devicePage.property("currentDevice")
            objectDevice = SQL().getSingleDeviceAtID(idDevice)[0]
            cloudMessage.sendMessageMqtt(
                [
                    PackData.PackValueDevice(
                        mac=objectDevice[2],
                        type=PackData.TypeDevice["Relay"],
                        action=PackData.TypeAction["Delete"],
                    )
                ],
                PackData.FormData["Device"],
            )
        else:
            objectDevice = SQL().getSingleDeviceAtMac(mac)[0]
            idDevice = objectDevice[0]
        deviceBLE = SQL().getDeviceBLE(idDevice + 50000)
        SQL().deleteDeviceAtMac(objectDevice[2])
        SQL().deleteActionDevice(idDevice)
        SQL().deleteDeviceBLE(idDevice)
        unicst = []
        for x in deviceBLE:
            unicst.append(x[2])
        bleMessage.resetNode(unicst)
        bleMessage.delGroup(unicst, idDevice + 50000)
        self.devicePage.findChild(QObject, "device" + str(idDevice)).delItem.emit()


class Sensor:
    """
    Class for Sensor Object
    """

    def __init__(self):
        self.sensorPage = engine.rootObjects()[0].findChild(QObject, "sensorPage")
        self.addSensor = engine.rootObjects()[0].findChild(QObject, "addSensor")
        self.addSensor.clicked.connect(lambda: self.seachSensor())
        self.sensorPage.seach.connect(lambda: self.addDevice())

    def showAllSensor(self):
        allSensor = sql.getMultiSensor()
        for singleSensor in allSensor:
            idSensor = singleSensor[0]
            self.sensorPage.addSensor(idSensor)
            self.showSensor(singleSensor)
            sensor = self.sensorPage.findChild(QObject, "sensor" + str(idSensor))
            sensor.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteSensor()
            )

    def showSensor(self, singleSensor):
        idSensor = singleSensor[0]
        if self.sensorPage.property("newSensor") is True:
            self.sensorPage.addSensor(idSensor)
            sensor = self.sensorPage.findChild(QObject, "sensor" + str(idSensor))
            sensor.findChild(QObject, "delete").clicked.connect(
                lambda: self.deleteSensor()
            )
            self.sensorPage.setProperty("newSensor", False)
        sensor = self.sensorPage.findChild(QObject, "sensor" + str(idSensor))
        sensor.setProperty("idSensor", singleSensor[0])
        sensor.setProperty("nameSensor", singleSensor[1])
        sensor.setProperty("macSensor", singleSensor[2])
        sensor.setProperty("typeSensor", singleSensor[4])
        sensor.setProperty("sensorValue", singleSensor[5])
        sensor.setProperty("batteryValue", singleSensor[6])

    def seachSensor(self):
        gatewayMessage.scanDevice()

    def addDevice(self):
        allSensor = SQL().getMultiSensor()
        for singleSensor in allSensor:
            idSensor = singleSensor[0]
            if (
                engine.rootObjects()[0].findChild(QObject, "sensor" + str(idSensor))
                is None
            ):
                self.sensorPage.setProperty("newSensor", True)
                self.showSensor(singleSensor)

    def deleteSensor(self, mac=None):
        """
        :param mac: mac of sensor
        :return:
        """
        if mac is None:
            idSensor = self.sensorPage.property("currentSensor")
            objectSensor = sql.getSingleSensorAtID(idSensor)[0]
            mac = objectSensor[2]
            cloudMessage.sendMessageMqtt(
                [
                    PackData.PackValueDevice(
                        mac=objectSensor[13],
                        type=PackData.TypeDevice["Sensor"],
                        action=PackData.TypeAction["Delete"],
                    )
                ],
                PackData.FormData["Device"],
            )
        objectSensor = SQL().getSingleSensorAtMac(mac)
        for singleSensor in objectSensor:
            self.sensorPage.findChild(
                QObject, "sensor" + str(singleSensor[0])
            ).delItem.emit()
            SQL().deleteConditionSensor(singleSensor[0])
        SQL().insertGatewayCommand(uni=objectSensor[0][3], active=1)
        SQL().deleteSensorAtMac(objectSensor[0][2])


class BLEMessage:
    """
    Class for BLE message
    """

    def __init__(self):
        self.cmd = None
        self.data = None
        self.idDevice = 49152
        self.PORT = [PORT_BLE, PORT_BLE, PORT_BLE, PORT_BLE]
        self.cmdScanDevice = {"CMD": "SCAN"}
        self.cmdStop = {"CMD": "STOP"}

    def load(self, message):
        """
        Load message for processing
        :param message: message from server
        :return: None
        """
        print("Message BLE:", message)
        logger.info(f"Message BLE:{message}")
        messageDecode = message.decode("utf-8")
        if (messageDecode in "device not found") is True:
            self.scanGW(0)
            return
        if (messageDecode in "device accepted") is True:
            ble.disconnect()
            ble.connect("localhost", 1883, 60)
            ble.loop_start()
            return
        messageJson = json.loads(messageDecode)
        self.idDevice = (
            engine.rootObjects()[0]
            .findChild(QObject, "devicePage")
            .property("currentScan")
        )
        for key, value in messageJson.items():
            if key == "CMD":
                self.cmd = messageJson["CMD"]
            elif key == "DATA":
                self.data = messageJson["DATA"]
        if (self.cmd in "NEW_DEVICE") is True:
            self._addNewDevice()
        elif (self.cmd in "ADDGROUP") is True:
            self._addGroupDone()
        elif (self.cmd in "STOP") is True:
            engine.rootObjects()[0].findChild(
                QObject, "device" + str(self.idDevice)
            ).setProperty("scanning", True)

    def _addNewDevice(self):
        unics = self.data["DEVICE_UNICAST_ID"]
        print("INSERT NEW DEVICE BLE", unics)
        logger.info(f"INSERT NEW DEVICE BLE {unics}")
        self._addGroup(unics)
        return

    def _addGroup(self, unics):
        cmdAddGroup = {
            "CMD": "ADDGROUP",
            "DATA": {
                "DEVICE_UNICAST_ID": [unics],
                "GROUP_UNICAST_ID": self.idDevice + 50000,
            },
        }
        publishBLE(cmdAddGroup)
        return

    def _addGroupDone(self):
        SQL().insertDeviceBLE(
            group=self.data["GROUP_UNICAST_ID"], unicast=self.data["DEVICE_UNICAST_ID"]
        )

    def _delGroupDone(self):
        SQL().deleteDeviceBLE(self.data["GROUP_UNICAST_ID"])

    def resetNode(self, unics):
        """
        Reset Node from BLE mesh
        :param unics:
        :return:
        """
        cmd = self.getCommand(cmd="RESETNODE", unics=unics)
        publishBLE(cmd)

    def delGroup(self, objectDevice, group):
        """
        :param objectDevice:
        :param group:
        :return:
        """
        cmd = self.getCommand(cmd="DELGROUP", objectDevice=objectDevice, group=group)
        publishBLE(cmd)

    def scanDevice(self):
        """
        Scan New Device
        :return:
        """
        publishBLE(self.cmdScanDevice)

    def scanGW(self, portNumber):
        """
        Scan gateway
        :param portNumber:
        :return:
        """
        cmdScanGW = {"CMD": "DEVICE_PORT", "DATA": {"PORT": self.PORT[portNumber]}}

        publishBLE(cmdScanGW)

    def controlONOFF(self, unics, pull):
        """
        :param unics:
        :param pull:
        """
        cmd = self.getCommand(cmd="ONOFF", unics=unics, pull=pull)
        publishBLE(cmd)
        cmd = self.getCommand(cmd="ONOFF", unics=unics, pull=pull)
        publishBLE(cmd)

    def controlDIM(self, unics, dim):
        """
        :param unics:
        :param dim:
        :return:
        """
        cmd = self.getCommand(cmd="DIM", unics=unics, dim=dim)
        publishBLE(cmd)
        cmd = self.getCommand(cmd="DIM", unics=unics, dim=dim)
        publishBLE(cmd)

    def controlCCT(self, unics, cct):
        """
        :param unics:
        :param cct:
        :return:
        """
        cmd = self.getCommand(cmd="CCT", unics=unics, cct=cct)
        publishBLE(cmd)
        cmd = self.getCommand(cmd="CCT", unics=unics, cct=cct)
        publishBLE(cmd)

    def getCommand(
        self,
        cmd=None,
        unics=None,
        objectDevice=None,
        group=None,
        pull=None,
        dim=None,
        cct=None,
    ):
        """
        :param cct:
        :param dim:
        :param pull:
        :param group:
        :param objectDevice:
        :param unics:
        :param cmd: Type Command
        :return: Json Command for BLE mesh
        """
        command = {}
        if (cmd in "ONOFF") is True:
            command = {
                "CMD": "ONOFF",
                "DATA": {"DEVICE_UNICAST_ID": unics, "VALUE_ONOFF": pull},
            }
        elif (cmd in "DIM") is True:
            command = {
                "CMD": "DIM",
                "DATA": {"DEVICE_UNICAST_ID": unics, "VALUE_DIM": dim},
            }
        elif (cmd in "CCT") is True:
            command = {
                "CMD": "CCT",
                "DATA": {"DEVICE_UNICAST_ID": unics, "VALUE_CCT": cct},
            }
        elif (cmd in "DELGROUP") is True:
            command = {
                "CMD": "DELGROUP",
                "DATA": {"DEVICE_UNICAST_ID": objectDevice, "GROUP_UNICAST_ID": group},
            }
        elif (cmd in "RESETNODE") is True:
            command = {"CMD": "RESETNODE", "DATA": {"DEVICE_UNICAST_ID": unics}}
        elif (cmd in "ADDGROUP") is True:
            command = {
                "CMD": "ADDGROUP",
                "DATA": {
                    "DEVICE_UNICAST_ID": [unics],
                    "GROUP_UNICAST_ID": self.idDevice + 50000,
                },
            }
        return command


class CloudMessage:
    """
    Class for message from server
    """

    def __init__(self):
        self.head = None
        self.device = None
        self.control = None
        self.rule = None
        self.timelinePage = engine.rootObjects()[0].findChild(QObject, "timelinePage")

    def load(self, message):
        """
        :param message: message from server
        :return:
        """
        for key, value in message.items():
            if key == "Head":
                self.head = value
                self._processHead()

            elif key == "Rule":
                self.rule = value
                self._processRule()
            elif key == "Device":
                self.device = value
                self._processDevice()
            elif key == "Control":
                self.control = value
                self._processControl()

    def _processDevice(self):
        for deviceOnGateway in self.device:
            if deviceOnGateway["Action"] == PackData.TypeAction["Scan"]:
                if deviceOnGateway["Type"] == PackData.TypeDevice["Sensor"]:
                    try:
                        sensorPage = engine.rootObjects()[0].findChild(
                            QObject, "sensorPage"
                        )
                        sensorPage.findChild(QObject, "addSensor").clicked.emit()
                    except:
                        continue
            elif deviceOnGateway["Action"] == PackData.TypeAction["Delete"]:
                macDevice = deviceOnGateway["ID"]
                if deviceOnGateway["Type"] == PackData.TypeDevice["Sensor"]:
                    try:
                        macSensor = SQL().getSingleSensorAtHash(macDevice)[0][2]
                        sensor.deleteSensor(mac=macSensor)
                    except:
                        print("Have not Sensor", macDevice, " for Delete")
                        continue
                else:
                    try:
                        device.deleteDevice(mac=macDevice)
                    except:
                        print("Have not Device", macDevice, " for Delete")
                        continue
            elif deviceOnGateway["Action"] == PackData.TypeAction["Update"]:
                macDevice = deviceOnGateway["ID"]
                if deviceOnGateway["Type"] == 0:
                    try:
                        SQL().updateNameSensor(
                            [
                                deviceOnGateway["Name"],
                                deviceOnGateway["ID"],
                                deviceOnGateway["TypeSensor"],
                            ]
                        )
                    except:
                        print("Has not Device For Update")
                        continue
                    try:
                        SQL().updateCalibSensor(
                            [
                                deviceOnGateway["Min"],
                                deviceOnGateway["Max"],
                                deviceOnGateway["Param_a"],
                                deviceOnGateway["Param_b"],
                                deviceOnGateway["Param_c"],
                                deviceOnGateway["Delay"],
                                deviceOnGateway["ID"],
                                deviceOnGateway["TypeSensor"],
                            ]
                        )
                        allSensor = SQL().getSingleSensorAtHash(macDevice)
                        for s in allSensor:
                            sensor.showSensor(s)
                    except:
                        print("Have not Calib")
                    try:
                        SQL().updateDelaySensor(
                            [deviceOnGateway["Delay"], deviceOnGateway["ID"]]
                        )
                    except:
                        print("update Delay Sensor error!")
                else:
                    try:
                        dataDevice = SQL().getSingleDeviceAtMac(macDevice)[0]
                    except:
                        print("Has not Device For Update")
                        continue
                    try:
                        SQL().updateNameDevice(
                            deviceOnGateway["Name"],
                            deviceOnGateway["Pin"] - 1,
                            dataDevice[0],
                        )
                        dataDevice = SQL().getSingleDeviceAtMac(macDevice)[0]
                        device.showDevice(dataDevice)
                    except:
                        print("Have not key Name")
                        continue
            elif deviceOnGateway["Action"] == PackData.TypeAction["Addition"]:
                typeDevice = 0
                pinDevice = deviceOnGateway["Pin"] - 1
                if deviceOnGateway["Type"] == PackData.TypeDevice["Relay"]:
                    typeDevice = 1
                try:
                    SQL().insertDevice(
                        [
                            deviceOnGateway["Name"],
                            deviceOnGateway["ID"],
                            str(random.randint(10000000, 100000000)),
                            False,
                            typeDevice,
                            pinDevice,
                            0,
                            0,
                            0,
                        ]
                    )
                except:
                    print("Error Addition Device:", deviceOnGateway["ID"])
                engine.rootObjects()[0].findChild(QObject, "devicePage").seach.emit()

    def _processControl(self):
        for control in self.control:
            macDevice = control["ID"]
            idDevice = SQL().getSingleDeviceAtMac(macDevice)[0][0]
            for key, value in control.items():
                if key == "Pull":
                    pull = value
                    try:
                        device.updateStatusDevice(
                            pull=pull, idDevice=idDevice, action=1
                        )
                    except:
                        continue
                elif key == "Dim":
                    dim = value
                    try:
                        device.updateDimDevice(dim=dim, idDevice=idDevice, action=1)
                    except:
                        continue
                elif key == "CCT":
                    cct = value
                    try:
                        device.updateCCTDevice(cct=cct, idDevice=idDevice, action=1)
                    except:
                        continue

    def _processHead(self):
        if self.head["TypeMessage"] == PackData.TypeMessage["Rep"]:
            data = PackData.PackHead(
                idMessage=self.head["IDMessage"],
                typeMess=PackData.TypeMessage["NotRep"],
                formData=PackData.FormData["Response"],
                mac=PackData.MacGateway,
            )
            publishMqtt(json.dumps({"Head": data}))

    def _processRule(self):
        for rule in self.rule:
            idRule = rule["ID"]
            typeRule = rule["Type"]
            actionRule = rule["Action"]
            active = None
            input = None
            exe = None
            name = None
            if actionRule == PackData.TypeAction["Delete"]:
                try:
                    self._deleteRule(idRule, typeRule)
                except:
                    continue
                continue
            for key, value in rule.items():
                print(key, value)
                if key == "Active":
                    active = value
                elif key == "Input":
                    input = value
                elif key == "Execute":
                    exe = value
                elif key == "Name":
                    name = value

            if actionRule == PackData.TypeAction["Addition"]:
                try:
                    self._addRule(
                        idRule=idRule,
                        typeRule=typeRule,
                        active=active,
                        name=name,
                        input=input,
                        exe=exe,
                    )
                except:
                    continue
            if actionRule == PackData.TypeAction["Update"]:
                try:
                    self._update(idRule, typeRule, active, input, exe, name)
                except:
                    continue

    def _deleteRule(self, idRule, typeRule):
        """
        :param idRule:
        :param typeRule:
        :return:
        """
        if typeRule == PackData.TypeRule["Schedule"]:
            try:
                timeline.deleteTimeline(idTimeline=idRule)
            except:
                print("Have not Timeline", idRule, " For Delete")
                logger.error(f"Have not Timeline {idRule} For Delete")
        elif typeRule == PackData.TypeRule["Rule"]:
            try:
                rules.deleteRules(idRules=idRule)
            except:
                print("Have not Rule", idRule, " For Delete")
                logger.error(f"Have not Rule {idRule} For Delete")
        elif typeRule == PackData.TypeRule["Script"]:
            try:
                script.deleteScript(idScript=idRule)
            except:
                print("Have not Script", idRule, " For Delete")
                logger.error(f"Have not Script {idRule} For Delete")

    def _addRule(self, idRule, typeRule, active=None, input=None, exe=None, name=None):
        if typeRule == PackData.TypeRule["Schedule"]:
            SQL().insertTimelineSql([idRule, name, active])
            SQL().insertConditionTimeline(
                [
                    idRule,
                    input["Schedule"]["TimeStart"],
                    input["Loop"]["Monday"],
                    input["Loop"]["Tuesday"],
                    input["Loop"]["Wednesday"],
                    input["Loop"]["Thursday"],
                    input["Loop"]["Friday"],
                    input["Loop"]["Saturday"],
                    input["Loop"]["Sunday"],
                ]
            )
            for x in exe:
                action = [idRule]
                action.append(SQL().getSingleDeviceAtMac(x["ID"])[0][0])
                action.append(x["Pull"])
                if x["Type"] == PackData.TypeDevice["Led"]:
                    action.append(x["Dim"])
                    action.append(x["CCT"])
                else:
                    action += [0, 0]
                SQL().insertActionTimeline(action)
            engine.rootObjects()[0].findChild(QObject, "timelinePage").seach.emit()
        elif typeRule == PackData.TypeRule["Rule"]:
            SQL().insertRulesSql([idRule, name, active])
            for x in input["Condition"]["Compare"]:
                try:
                    # idSensor = SQL().getSingleSensorAtHash(x["ID"])[0][0]
                    idSensor = SQL().getSingleSensorAtHashType(
                        x["ID"], x["TypeSensor"]
                    )[0][0]
                    SQL().insertConditionRules(
                        [idRule, idSensor, x["Equal"], x["Value"]]
                    )
                except:
                    print("Have not Sensor", x["ID"], "For Condition Rule")
                    logger.error(f"Have not Sensor {x['ID']} For Condition Rule")
            SQL().insertConditionRules2(
                [
                    idRule,
                    input["Schedule"]["TimeStart"],
                    input["Schedule"]["TimeStop"],
                    input["Schedule"]["TimeUpdate"],
                    input["Loop"]["Monday"],
                    input["Loop"]["Tuesday"],
                    input["Loop"]["Wednesday"],
                    input["Loop"]["Thursday"],
                    input["Loop"]["Friday"],
                    input["Loop"]["Saturday"],
                    input["Loop"]["Sunday"],
                    input["Condition"]["Logic"],
                ]
            )
            SQL().insertConditionRules3([idRule, 0, 0, 0])
            for x in exe:
                if x["Type"] == PackData.TypeDevice["Script"]:
                    SQL().insertActionRules([idRule, False, x["ID"], 1, 0, 0, 0, 0])
                elif x["Type"] == PackData.TypeDevice["Relay"]:
                    idDevice = SQL().getSingleDeviceAtMac(x["ID"])[0][0]
                    SQL().insertActionRules(
                        [idRule, True, idDevice, 1, 0, 0, x["Delay"], x["During"]]
                    )
                elif x["Type"] == PackData.TypeDevice["Led"]:
                    idDevice = SQL().getSingleDeviceAtMac(x["ID"])[0][0]
                    SQL().insertActionRules(
                        [
                            idRule,
                            True,
                            idDevice,
                            1,
                            x["Dim"],
                            x["CCT"],
                            x["Delay"],
                            x["During"],
                        ]
                    )
            engine.rootObjects()[0].findChild(QObject, "rulesPage").seach.emit()
        elif typeRule == PackData.TypeRule["Script"]:
            SQL().insertScript([idRule, name, 0])
            SQL().insertConditionScript([idRule, 0, 0])
            for x in exe:
                idDevice = SQL().getSingleDeviceAtMac(x["ID"])[0][0]
                action = [idRule, idDevice, 1]
                if x["Type"] == PackData.TypeDevice["Relay"]:
                    action += [0, 0]
                else:
                    action += [x["Dim"], x["CCT"]]
                action += [x["Delay"], x["During"], 0]
                SQL().insertActionScript(action)
            engine.rootObjects()[0].findChild(QObject, "scriptPage").seach.emit()

    def _update(self, idRule, typeRule, active=None, input=None, exe=None, name=None):
        if typeRule == PackData.TypeRule["Schedule"]:
            if active is not None:
                timeline.updateActiveTimeline(active, idRule, 1)
            if input is not None:
                try:
                    SQL().updateTimelineSql([name, idRule])
                except:
                    print("Have not Timeline", idRule, "For Delete")
                    logger.error(f"Have not Timeline {idRule} For Delete")
                    return
                SQL().deleteConditionTimeline(idRule)
                SQL().deleteActionTimeline(idRule)
                SQL().insertConditionTimeline(
                    [
                        idRule,
                        input["Schedule"]["TimeStart"],
                        input["Loop"]["Monday"],
                        input["Loop"]["Tuesday"],
                        input["Loop"]["Wednesday"],
                        input["Loop"]["Thursday"],
                        input["Loop"]["Friday"],
                        input["Loop"]["Saturday"],
                        input["Loop"]["Sunday"],
                    ]
                )
                for x in exe:
                    action = [idRule]
                    action += [SQL().getSingleDeviceAtMac(x["ID"])[0][0], x["Pull"]]
                    if x["Type"] == PackData.TypeDevice["Led"]:
                        action += [x["Dim"], x["CCT"]]
                    else:
                        action += [0, 0]
                    SQL().insertActionTimeline(action)
                engine.rootObjects()[0].findChild(
                    QObject, "timeline" + str(idRule)
                ).setProperty("nameAction", name)

        if typeRule == PackData.TypeRule["Rule"]:
            if active is not None:
                rules.updateActiveRules(idRule, active)
            if input is not None and exe is not None:
                SQL().updateRulesSql([name, idRule])
                SQL().deleteConditionRules(idRule)
                SQL().deleteConditionRules2(idRules=idRule)
                SQL().deleteActionRules(idRule)
                SQL().insertConditionRules2(
                    [
                        idRule,
                        input["Schedule"]["TimeStart"],
                        input["Schedule"]["TimeStop"],
                        input["Schedule"]["TimeUpdate"],
                        input["Loop"]["Monday"],
                        input["Loop"]["Tuesday"],
                        input["Loop"]["Wednesday"],
                        input["Loop"]["Thursday"],
                        input["Loop"]["Friday"],
                        input["Loop"]["Saturday"],
                        input["Loop"]["Sunday"],
                        input["Condition"]["Logic"],
                    ]
                )
                for x in input["Condition"]["Compare"]:
                    # idSensor = SQL().getSingleSensorAtHash(x["ID"])[0][0]
                    idSensor = SQL().getSingleSensorAtHashType(
                        x["ID"], x["TypeSensor"]
                    )[0][0]
                    SQL().insertConditionRules(
                        [idRule, idSensor, x["Equal"], x["Value"]]
                    )
                for x in exe:
                    if x["Type"] == PackData.TypeDevice["Script"]:
                        SQL().insertActionRules([idRule, 0, x["ID"], 1, 0, 0, 0, 0])
                    elif x["Type"] == PackData.TypeDevice["Relay"]:
                        idDevice = SQL().getSingleDeviceAtMac(x["ID"])[0][0]
                        SQL().insertActionRules(
                            [idRule, 1, idDevice, 1, 0, 0, x["Delay"], x["During"]]
                        )
                    elif x["Type"] == PackData.TypeDevice["Led"]:
                        idDevice = SQL().getSingleDeviceAtMac(x["ID"])[0][0]
                        SQL().insertActionRules(
                            [
                                idRule,
                                1,
                                idDevice,
                                1,
                                x["Dim"],
                                x["CCT"],
                                x["Delay"],
                                x["During"],
                            ]
                        )
                engine.rootObjects()[0].findChild(
                    QObject, "rules" + str(idRule)
                ).setProperty("nameAction", name)
        if typeRule == PackData.TypeRule["Script"]:
            if active is not None:
                print("Active Script")
                script.updateActiveScript(idScript=idRule, active=active, action=1)
            if input is not None and exe is not None:
                SQL().updateScript([name, idRule])
                SQL().deleteActionScript(idRule)
                for x in exe:
                    idDevice = SQL().getSingleDeviceAtMac(x["ID"])[0][0]
                    action = [idRule, idDevice, 1]
                    if x["Type"] == PackData.TypeDevice["Relay"]:
                        action += [0, 0]
                    else:
                        action += [x["Dim"], x["CCT"]]
                    action += [x["Delay"], x["During"], 0]
                    SQL().insertActionScript(action)
                engine.rootObjects()[0].findChild(
                    QObject, "script" + str(idRule)
                ).setProperty("nameAction", name)

    def sendMessageMqtt(self, message, typePackage):
        idMessage = random.randint(20000000, 300000000)
        data = []
        if typePackage == PackData.FormData["Sensor"]:
            data = PackData.PackSensor(idMessage, message)
        elif typePackage == PackData.FormData["Device"]:
            data = PackData.PackDevice(idMessage, message)
        elif typePackage == PackData.FormData["Control"]:
            data = PackData.PackControl(idMessage, message)
        elif typePackage == PackData.FormData["Rule"]:
            data = PackData.PackTRS(idMessage, message)
        publishMqtt(data)


class GatewayMessage:
    """
    Class for gateway message
    """

    def __init__(self):
        self._serial = serial.Serial()
        self._serial.baudrate = BAUD_GW
        self._serial.port = PORT_GW
        self._serial.timeout = 1
        self._waitScan = QTimer(app)
        self._resetGWTimer = QTimer(app)
        self._waitScan.timeout.connect(lambda: self.stopScanDevice())
        self._resetGWTimer.timeout.connect(lambda: self.resetGW())
        self._resetGWTimer.start(600000)
        self._gTempSensorValue = 0
        self._gLightSensorValue = 0
        self._gSoilSensorValue = 0
        self._gCSensorValue = 0
        try:
            self._serial.open()
        except:
            print("Fail serial Port!")
            logger.error("Fail serial Port!")

        print("Serial is Open:", self._serial.isOpen())
        logger.info(f"Serial is Open: {self._serial.isOpen()}")
        if self._serial.isOpen() is False:
            self._serial.open()

    def scanDevice(self):
        self._resetGWTimer.stop()
        cmd = [0xAA, 0x01]
        cmd += [self._checkSum(cmd), 0x09, 0x0A]
        print(cmd)
        self._serial.write(bytes(cmd))
        self._waitScan.start(30000)
        engine.rootObjects()[0].findChild(QObject, "sensorPage").setProperty(
            "scanSensor", False
        )
        self._resetGWTimer.start(600000)

    def stopScanDevice(self):
        cmd = [0xAA, 0x02]
        cmd += [self._checkSum(cmd), 0x09, 0x0A]
        print(cmd)
        self._serial.write(bytes(cmd))
        self._waitScan.stop()
        engine.rootObjects()[0].findChild(QObject, "sensorPage").setProperty(
            "scanSensor", True
        )

    def resetGW(self):
        cmd = [
            0xAA,
            0x08,
        ]
        cmd += [self._checkSum(cmd), 0x09, 0x0A]
        self._serial.write(bytes(cmd))

    def deleteDevice(self, uni):
        uniList = list(bytes(uni, "ascii"))
        cmd = [0xAA, 0x02] + uniList
        cmd.append(self._checkSum(cmd))
        cmd.append(0x09)
        cmd.append(0x0A)
        print(cmd)
        self._serial.writelines(bytes(cmd))

    def _addDevice(self, value):
        self.stopScanDevice()
        mac = ""
        for i in range(2, 10, 1):
            mac += chr(value[i])
        uni = ""
        for i in range(10, 14, 1):
            uni += chr(value[i])
        type = value[14]
        name = ""
        minVal = 0
        maxVal = 100
        if type == 0:
            name = "Nhiet do "
            minVal = -20
            maxVal = 100
        elif type == 2:
            name = "Do am dat "
            minVal = 0
            maxVal = 100
        elif type == 3:
            name = "Anh Sang "
            minVal = 0
            maxVal = 100000
        elif type == 4:
            name = "CO2 "
            minVal = 400
            maxVal = 8192
        number = str(random.randint(0, 100000))
        SQL().insertSensor(
            [name + number, mac, uni, type, 0, 100, minVal, maxVal, 1, 0, 0, 5, number]
        )
        valueDevice = PackData.PackValueDevice(
            mac=number,
            type=PackData.TypeDevice["Sensor"],
            typesensor=type,
            name=name + number,
            value=0,
            battery=100,
            max=maxVal,
            min=minVal,
            par_a=1,
            par_b=0,
            par_c=0,
            delay=10,
            action=PackData.TypeAction["Addition"],
        )
        cloudMessage.sendMessageMqtt([valueDevice], PackData.FormData["Device"])
        if type == 0:
            minVal = 0
            maxVal = 100
            SQL().insertSensor(
                [
                    "Do am " + number,
                    mac,
                    uni,
                    1,
                    0,
                    100,
                    minVal,
                    maxVal,
                    1,
                    0,
                    0,
                    5,
                    number,
                ]
            )
            valueDevice1 = PackData.PackValueDevice(
                mac=number,
                type=PackData.TypeDevice["Sensor"],
                typesensor=1,
                name="Do Am " + number,
                value=0,
                battery=100,
                max=maxVal,
                min=minVal,
                par_a=1,
                par_b=2,
                par_c=3,
                action=PackData.TypeAction["Addition"],
            )
            cloudMessage.sendMessageMqtt([valueDevice1], PackData.FormData["Device"])
        engine.rootObjects()[0].findChild(QObject, "sensorPage").seach.emit()

    def getCommandLora(self):
        while True:
            value = []
            try:
                value = self._serial.read_until([0x09, 0x0A])
            except:
                print("Read bytes error")
                logger.error("Read bytes error")
                continue
            length = len(value)
            if length < 5 or length > 25:
                continue
            value = list(value)
            value = value[0 : length - 2]
            print(value)
            logger.info(f"Serial Data: {value}")
            try:
                if value[0] != 170:
                    print("Wrong Frame data")
                    logger.error("Wrong Frame data")
                    continue
            except:
                print("Value Fail!")
                logger.error("Value Fail!")
                continue
            if self._checkSum(value[0 : len(value) - 1]) != value[len(value) - 1]:
                print("Check Sum error")
                logger.error("Check Sum error")
                continue
            if value[1] == 0x04 or value[1] == 0x05 or value[1] == 0x07:
                self._updateSensorType1(value)
            elif value[1] == 0x06:
                self._updateSensorType2(value)
            elif value[1] == 0x01:
                self._addDevice(value)
            elif value[1] == 0x02:
                unicast = chr(value[2]) + chr(value[3]) + chr(value[4]) + chr(value[5])
                SQL().deleteGatewayCommand(unicast)

    def _updateSensorType2(self, value, minval=None):
        unicast = chr(value[2]) + chr(value[3]) + chr(value[4]) + chr(value[5])
        temp = struct.unpack(">f", bytes(value[6:10]))[0] / 10
        hum = struct.unpack(">f", bytes(value[10:14]))[0] / 10
        battery = int(value[14])
        command = [0xAA, 0x04] + list(bytes(unicast, "ascii"))
        if temp == 0 and self._gTempSensorValue != 0:
            self._gTempSensorValue = temp
            self._serialSend(command)
            return
        else:
            self._gTempSensorValue = temp
        if len(SQL().getGatewayCommand(unicast)) != 0:
            command += [1, 0]
            print("Delete unicast:", unicast)
            logger.info(f"Delete unicast: {unicast}")
            SQL().deleteGatewayCommand(unicast)
        else:
            try:
                AllSensor = SQL().getSingleSensorAtUni(unicast)
                for singleSensor in AllSensor:
                    typeSensor = singleSensor[4]
                    a = singleSensor[9]
                    b = singleSensor[10]
                    minVal = singleSensor[7]
                    maxVal = singleSensor[8]
                    if typeSensor == 0:
                        temp = temp * a + b
                        if temp < minVal:
                            temp = minVal
                        elif temp > maxVal:
                            temp = maxVal
                        temp = round(temp, 2)
                    elif typeSensor == 1:
                        hum = hum * a + b
                        if hum < minVal:
                            hum = minVal
                        elif hum > maxVal:
                            hum = maxVal
                        hum = round(hum, 2)
                SQL().updateBatterySensor(battery, unicast)
                SQL().updateValueSensorAtType(temp, unicast, 0)
                SQL().updateValueSensorAtType(hum, unicast, 1)
            except:
                print("Update value Sensor 1 Fail!")
                logger.error("Update value Sensor 1 Fail!")
                return
            sensorTemp = SQL().getSingleSensorAtUni(unicast)
            if len(sensorTemp) == 0:
                print("Update value Sensor 1 Fail!")
                logger.error("Update value Sensor 1 Fail!")
                return
            message = [
                PackData.PackValueSensor(
                    sensorTemp[0][13], PackData.TypeSensor["Temp"], temp, battery
                ),
                PackData.PackValueSensor(
                    sensorTemp[1][13], PackData.TypeSensor["Hum"], hum, battery
                ),
            ]
            cloudMessage.sendMessageMqtt(message, PackData.FormData["Sensor"])
            for s in sensorTemp:
                sensor.showSensor(s)
            singleSensor = sensorTemp[0]
            command += [0, singleSensor[12]]
        command += [self._checkSum(command), 0x09, 0x0A]
        self._serialSend(command)

    def _updateSensorType1(self, value):
        unicast = chr(value[2]) + chr(value[3]) + chr(value[4]) + chr(value[5])
        valueSensor = int.from_bytes(value[6:10], "little")
        batterySensor = int(value[10])
        typeSensor = 2
        command = [0xAA, 0x04] + list(bytes(unicast, "ascii"))
        if len(SQL().getGatewayCommand(unicast)) != 0:
            print("Delete device:", unicast)
            logger.info(f"Delete device: {unicast}")
            command += [1, 0]
            SQL().deleteGatewayCommand(unicast)
        else:
            if value[1] == 0x04:
                typeSensor = PackData.TypeSensor["Light"]
                print(f"gLightSensorValue: {self._gLightSensorValue}")
                print(f"Value Sensor: {valueSensor}")
                if valueSensor == 0 and self._gLightSensorValue != 0:
                    self._gLightSensorValue = valueSensor
                    self._serialSend(command)
                    return
                else:
                    self._gLightSensorValue = valueSensor
            elif value[1] == 0x05:
                typeSensor = PackData.TypeSensor["Soil"]
                print(f"gSoilSensorValue: {self._gSoilSensorValue}")
                print(f"Value Sensor: {valueSensor}")
                if valueSensor == 0 and self._gSoilSensorValue != 0:
                    self._gSoilSensorValue = valueSensor
                    self._serialSend(command)
                    return
                else:
                    self._gSoilSensorValue = valueSensor
            elif value[1] == 0x07:
                typeSensor = PackData.TypeSensor["CO2"]
                print(f"gCSensorValue: {self._gCSensorValue}")
                print(f"Value Sensor: {valueSensor}")
                if valueSensor == 0 and self._gCSensorValue != 0:
                    self._gCSensorValue = valueSensor
                    command += [self._checkSum(command), 0x09, 0x0A]
                    self._serialSend(command)
                    return
                else:
                    self._gCSensorValue = valueSensor
                    batterySensor = value[14]
            try:
                try:
                    singleSensor = SQL().getSingleSensorAtUni(unicast)[0]
                    a = singleSensor[9]
                    b = singleSensor[10]
                    minVal = singleSensor[7]
                    maxVal = singleSensor[8]
                    valueSensor = valueSensor * a + b
                    if valueSensor < minVal:
                        valueSensor = minVal
                    elif valueSensor > maxVal:
                        valueSensor = maxVal
                    valueSensor = round(valueSensor, 2)
                except:
                    print("Have not sensor for update value")
                    logger.error("Have not sensor for update value")
                SQL().updateValueSensor(valueSensor, unicast)
                SQL().updateBatterySensor(batterySensor, unicast)
            except:
                print("Update Value Sensor 1 Fail!")
                logger.error("Update Value Sensor 1 Fail!")
                return
            AllSensor = SQL().getSingleSensorAtUni(unicast)
            if len(AllSensor) == 0:
                print("Have not sensor!")
                logger.info("Have not sensor!")
                return
            print(f"VALUE SENSOR: {valueSensor}")
            logger.info(f"VALUE SENSOR: {valueSensor}")
            message = [
                PackData.PackValueSensor(
                    AllSensor[0][13], typeSensor, valueSensor, batterySensor
                )
            ]
            cloudMessage.sendMessageMqtt(message, PackData.FormData["Sensor"])
            for s in AllSensor:
                print("Show Sensor Value:", s)
                logger.info(f"Show Sensor Value: {s}")
                sensor.showSensor(s)
            singleSensor = SQL().getSingleSensorAtUni(unicast)[0]
            command += [0, singleSensor[12]]
        self._serialSend(command)

    def _checkSum(self, command=None):
        if command is None:
            return
        sumData = 0
        for x in command:
            sumData = sumData ^ x
        return sumData

    def _serialSend(self, command):
        command += [self._checkSum(command), 0x09, 0x0A]
        print(command)
        try:
            logger.info(f"Serial Send Data: {command}")
            self._serial.write(bytes(command))
        except Exception as e:
            print(f"Exception While Sending Serial Data: {e}")
            logger.error(f"Exception While Sending Serial Data: {e}")


def runTimeline():
    """
    Run timeline
    :return: None
    """
    allTimeline = SQL().getMultiTimelineSql()
    for singleTimeline in allTimeline:
        idTimeline = singleTimeline[0]
        nameTimeline = singleTimeline[1]
        active = singleTimeline[2]
        if active == 0:
            print(f"Timeline: {nameTimeline} -Disable")
            logger.info(f"Timeline: {nameTimeline} -Disable")
            continue
        condition = []
        try:
            condition = SQL().getConditionTimeline(idTimeline)[0]
        except:
            print("Error get Condition Timeline!")
            logger.error("Error get Condition Timeline!")
            continue
        datetimeNow = datetime.now()
        """
            Check Weekday
        """
        if condition[datetimeNow.weekday() + 3] != 1:
            print("Timeline: {nameTimeline} -Not Run Today")
            logger.info(f"Timeline: {nameTimeline} -Not Run Today")
            continue
        """
            Check Time Run Action
        """
        timeNow = datetimeNow.hour * 3600 + datetimeNow.minute * 60
        if timeNow != condition[2]:
            print(f"Timeline: {nameTimeline} -Not Run Now")
            logger.info(f"Timeline: {nameTimeline} -Not Run Now")
            continue
        action = []
        try:
            action = SQL().getActionTimeline(idTimeline)[0]
        except:
            print("Error get Action Timeline!")
            logger.error("Error get Action Timeline!")
            continue
        pull = action[3]
        dim = action[4]
        cct = action[5]
        idDevice = action[2]
        try:
            singleDevice = SQL().getSingleDeviceAtID(idDevice)[0]
            isRelay = singleDevice[5]
            device.updateStatusDevice(pull=pull, idDevice=idDevice, action=2)
            if isRelay == 0:
                device.updateDimDevice(dim=dim, idDevice=idDevice, action=2)
                device.updateCCTDevice(cct=cct, idDevice=idDevice, action=2)
        except:
            continue


def runActionRule():
    """
    Run Rule
    :return:
    """
    allRules = SQL().getMultiRulesSql()
    for singleRules in allRules:
        idRules = singleRules[0]
        nameRules = singleRules[1]
        condition = []
        try:
            condition = SQL().getConditionRules3(idRules)
        except:
            print("Error get Condition Rule:", nameRules)
            logger.error(f"Error get Condition Rule: {nameRules}")
            continue
        run = condition[4]
        timeStart = condition[2]
        timeStop = condition[3]
        if run == 0:
            print("Action Rules:", nameRules, "-Not Run!")
            logger.info(f"Action Rules: {nameRules} -Not Run!")
            continue
        datetimeNow = datetime.now()
        timeNow = datetimeNow.hour * 3600 + datetimeNow.minute * 60
        print("Start:", timeStart, "TimeNow:", timeNow, "Stop:", timeStop)
        allAction = []
        try:
            allAction = SQL().getActionRules(idRules)
        except:
            print("Error get Action Rule:", nameRules)
            logger.error(f"Error get Action Rule: {nameRules}")
            continue
        for singleAction in allAction:
            if singleAction[2] == 0:
                continue
            idAction = singleAction[3]
            pull = singleAction[4]
            dim = singleAction[5]
            cct = singleAction[6]
            delay = singleAction[7]
            during = singleAction[8]
            singleDevice = []
            try:
                singleDevice = SQL().getSingleDeviceAtID(idAction)[0]
            except:
                print("Error get Device for Rule:", idAction)
                logger.error(f"Error get Device for Rule: {idAction}")
                continue
            if (
                timeNow != timeStart + delay * 60
                and timeNow != timeStart + (delay + during) * 60
            ):
                print("Not Time For Action Rules:", singleDevice[1])
                logger.info(f"Not Time For Action Rules: {singleDevice[1]}")
                continue
            if timeNow == timeStart + (delay + during) * 60:
                pull = 0
                dim = 0
                cct = 0
            try:
                if during == 0:
                    device.updateStatusDevice(pull=0, idDevice=idAction, action=2)
                else:
                    device.updateStatusDevice(pull=pull, idDevice=idAction, action=2)
                    if singleDevice[5] == 0:
                        device.updateDimDevice(dim=dim, idDevice=idAction, action=2)
                        device.updateCCTDevice(cct=cct, idDevice=idAction, action=2)
            except:
                continue
        if timeNow >= timeStop:
            print("Stop Action Rules:", nameRules)
            logger.info(f"Stop Action Rules: {nameRules}")
            SQL().updateConditionRules3(run=0, idRules=idRules)
            continue


def runScript():
    """
    Run Script
    :return: None
    """
    allScript = SQL().getMultiScript()
    for singleScript in allScript:
        idScrip = singleScript[0]
        nameScript = singleScript[1]
        activeScript = singleScript[2]
        if activeScript == 0:
            print("Script:", nameScript, "-Disable")
            continue
        try:
            conditionScript = SQL().getConditionScript(idScrip)[0]
        except:
            print("Error get Condition for Script:", nameScript)
            logger.error(f"Error get Condition for Script: {nameScript}")
            continue
        timeStart = conditionScript[2]
        timeStop = conditionScript[3]
        datetimeNow = datetime.now()
        timeNow = datetimeNow.hour * 3600 + datetimeNow.minute * 60 + datetimeNow.second
        action = []
        try:
            action = SQL().getActionScript(idScrip)
        except:
            print("Error get Action Script:", nameScript)
            logger.error(f"Error get Action Script: {nameScript}")
            continue
        for singleAction in action:
            idDevice = singleAction[2]
            delay = singleAction[6]
            during = singleAction[7]
            run = singleAction[8]
            pull = 1
            dim = singleAction[4]
            cct = singleAction[5]
            singleDevice = []
            try:
                singleDevice = SQL().getSingleDeviceAtID(idDevice)[0]
            except:
                print("Error get Device for Script:", nameScript)
                logger.error(f"Error get Device for Script: {nameScript}")
                continue
            typeRun = 0
            print("Run Action Script", run)
            if delay != 0 or during != 0:
                if delay * 60 + timeStart - 4 <= timeNow <= delay * 60 + timeStart + 4:
                    if run == 1:
                        typeRun = 1
                        SQL().updateRunActionScript(status=0, idAction=singleAction[0])
                elif (
                    (delay + during) * 60 + timeStart - 4
                    <= timeNow
                    <= (delay + during) * 60 + timeStart + 4
                ):
                    typeRun = 2
                    pull = 0
                    dim = 0
                    cct = 0
            else:
                typeRun = 3
            if typeRun == 0:
                print(
                    "Not Time For Action Script", nameScript, "Device", singleDevice[1]
                )
                continue
            try:
                if during == 0:
                    device.updateStatusDevice(pull=0, idDevice=idDevice, action=2)
                else:
                    device.updateStatusDevice(pull=pull, idDevice=idDevice, action=2)
                    if singleDevice[5] == 0:
                        device.updateDimDevice(dim=dim, idDevice=idDevice, action=2)
                        device.updateCCTDevice(cct=cct, idDevice=idDevice, action=2)
            except:
                continue
        if timeStop - 4 <= timeNow <= timeStop + 4 or timeStart == timeStop:
            script.updateActiveScript(idScript=idScrip, active=0, action=2)


def runRule():
    """
    Run Rule
    :return:
    """
    allRules = SQL().getMultiRulesSql()
    for singleRules in allRules:
        idRules = singleRules[0]
        nameRules = singleRules[1]
        active = singleRules[2]
        datetimeNow = datetime.now()
        if active == 0:
            print("Rules:", nameRules, "-Disable")
            continue
        try:
            conditionRule2 = SQL().getConditionRules2(idRules)[0]
        except:
            print("Error get condition Rule2:", nameRules)
            logger.error(f"Error get condition Rule2: {nameRules}")
            continue
        if conditionRule2[datetimeNow.weekday() + 5] != 1:
            print("Rules:", nameRules, "-Not Run Weekday ")
            continue
        timeNow = datetimeNow.hour * 3600 + datetimeNow.minute * 60
        timeStart = conditionRule2[2]
        timeStop = conditionRule2[3]
        timeUpdate = conditionRule2[4]
        logic = conditionRule2[12]
        if timeNow < timeStart or timeNow > timeStop:
            print("Rules:", nameRules, "-Not Run Now")
            continue
        if (timeNow - timeStart) % (timeUpdate * 60) != 0:
            print("Rules:", nameRules, "-Not Run Time Update")
            continue
        condition = []
        try:
            condition = SQL().getConditionRules(singleRules[0])
        except:
            print("Error get condition Rule:", nameRules)
            logger.error(f"Error get condition Rule: {nameRules}")
            continue
        compare = 0
        for singleCondition in condition:
            idSensor = singleCondition[2]
            conditionCompare = singleCondition[3]
            valueCompare = singleCondition[4]
            valueSensor = SQL().getSingleSensorAtID(idSensor)[0][5]
            if conditionCompare == 0:
                if valueSensor < valueCompare:
                    compare += 1
                else:
                    compare += 0
            else:
                if valueSensor > valueCompare:
                    compare += 1
                else:
                    compare += 0
        if logic == 0 and compare != len(condition):
            print("Rules:", nameRules, "-Condition is not satisfied")
            continue
        if logic == 1 and compare == 0:
            print("Rules:", nameRules, "-Condition is not satisfied")
            continue
        # condition3 = []
        # try:
        # condition3 = SQL().getConditionRules3(idRules)
        # except:
        # print("Error get condition3 Rule:", nameRules)
        # continue
        # if condition3[4] == 1:
        # print("Rule:", nameRules, "is running!")
        # continue
        action = []
        try:
            action = SQL().getActionRules(id=idRules)
        except:
            print("Error get action Rule:", nameRules)
            logger.error(f"Error get action Rule: {nameRules}")
            continue
        for singleAction in action:
            if singleAction[2] == 0:
                try:
                    script.updateActiveScript(
                        idScript=singleAction[3], active=1, action=2
                    )
                except:
                    continue
        if len(action) != 0:
            SQL().updateConditionRules3(run=1, idRules=idRules)


def configureTimer():
    """
    Configure Timer
    :return:
    """
    application = engine.rootObjects()[0]
    timelineTimer = QTimer(application)
    rulesTimer = QTimer(application)
    scriptTimer = QTimer(application)
    startTimer = QTimer(application)
    actionRuleTimer = QTimer(application)
    syncTimer = QTimer(application)

    timelineTimer.timeout.connect(lambda: runTimeline())
    scriptTimer.timeout.connect(lambda: runScript())
    rulesTimer.timeout.connect(lambda: runRule())
    startTimer.timeout.connect(lambda: runTimer())
    actionRuleTimer.timeout.connect(lambda: runActionRule())
    syncTimer.timeout.connect(lambda: sync())

    startTimer.start(1000)
    scriptTimer.start(5000)

    syncTimer.start(3600000)
    print("Start Configure Timer!")

    def runTimer():
        """
        Run Timer when begin new minute
        :return:
        """
        print("Check Configure Timer!")
        datetimeNow = datetime.now()
        if 0 < datetimeNow.second < 3:
            print("Stop Configure Timer!")
            startTimer.stop()
            timelineTimer.start(60000)
            rulesTimer.start(60000)
            sleep(15)
            actionRuleTimer.start(60000)


def configureThread():
    """
    Configure Multi Thread
    :return:
    """
    application = engine.rootObjects()[0]
    application.ScanGateway = ScanLoraGateway()
    application.ScanGateway.started.connect(lambda: application.ScanGateway.run)
    application.ScanGateway.start()
    application.ScanConnect = ScanReconnectMQTT()
    application.ScanConnect.started.connect(lambda: application.ScanConnect.run)
    application.ScanConnect.start()


def configureMQTT_MAC():
    """
    Configure connect to MQTT Server
    :return:None
    """
    setting = engine.rootObjects()[0].findChild(QObject, "setting")
    try:
        mac = open("/sys/firmware/devicetree/base/serial-number").read()
        PackData.MacGateway = mac[0:16]
    except:
        print("Cannot get new MAC")
        logger.error("Cannot get new MAC")
        mac = "fc:aa:14:6d:42:9a"
        PackData.MacGateway = mac
    setting.setProperty("ip", IP_SERVER)
    setting.setProperty("port", PORT_SERVER)
    setting.setProperty("mac", str(mac))
    setting.sync.connect(lambda: syncAll(1, 1, 1, 1, 1))
    connectMQTT_SERVER()
    connectMQTT_BLE()
    connectMQTT_OTA()
    print("IP:", IP_SERVER)
    print("MAC:", mac)
    logger.info(f"IP: {IP_SERVER} MAC: {mac}")


def reconnectMQTT():
    """
    :return:
    """
    print("Reconnect MQTT SERVER:", PORT_SERVER)
    logger.info(f"Reconnect MQTT SERVER: {PORT_SERVER}")
    connectMQTT_SERVER()
    connectMQTT_OTA()


def connectMQTT_BLE():
    """
    :return:
    """

    def on_connect(bleLed, userdata, flags, rc):
        """
        :param rc:
        :param flags:
        :param userdata:
        :param bleLed:
        :return:
        """
        print("Connected with MQTT BLE")
        logger.info("Connected with MQTT BLE")
        bleLed.subscribe("RD_STATUS")

    def on_message(ble, userdata, msg):
        """
        :param userdata:
        :param ble:
        :param msg:
        :return:
        """
        bleMessage.load(msg.payload)
        logger.info(f"Data BLE From {msg.topic}: {msg.payload}")

    ble.on_connect = on_connect
    ble.on_message = on_message
    ble.username_pw_set("RD", "1")
    ble.connect("localhost", 1883, 60)
    ble.loop_start()


def connectMQTT_SERVER():
    """
    :param ip:
    :return:
    """

    def on_connect(clientMQTT, userdata, flags, rc):
        """
        :param rc:
        :param flags:
        :param userdata:
        :param clientMQTT:
        :return:
        """
        print("Connected with MQTT SERVER")
        logger.info("Connected with MQTT SERVER")
        clientMQTT.subscribe(PackData.MacGateway + "host")
        publishMqtt("Connected")
        sync()

    def on_message(client, userdata, msg):
        """
        :param userdata:
        :param client:
        :param msg:
        :return:
        """
        print(msg.topic, msg.payload)
        logger.info(f"Data From Server - Topic: {msg.topic}: {msg.payload}")
        cloudMessage.load(json.loads(msg.payload))

    def on_disconnect(client, userdata, rc):
        """
        :param userdata:
        :param client:
        :param rc:
        :return:
        """
        print("Disconnecting reason  " + str(rc))
        logger.info(f"Disconnecting reason {str(rc)}")
        client.disconnect()

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.username_pw_set(USER_SERVER, PASS_SERVER)
    try:
        client.connect(IP_SERVER, PORT_SERVER, 60)
    except:
        print("Can Not Connect MQTT!")
        logger.error("Can Not Connect MQTT!")

    client.loop_start()


def connectMQTT_OTA():
    """
    :return:
    """

    def ChangeFile(data):
        """
        :param data:
        :return:
        """
        idMess = None
        fileUpdate = None
        syncGW = None
        action = None
        for key, value in data.items():
            print(key, value)
            if key == "ID":
                idMess = value
            elif key == "File":
                fileUpdate = value
            elif key == "Sync":
                syncGW = value
            elif key == "Action":
                action = value

        if fileUpdate is not None:
            m = hashlib.sha1()
            data = bytes(fileUpdate["Content"])
            m.update(data)
            h = m.hexdigest()
            if fileUpdate["Hash"] == h:
                f = open(fileUpdate["Name"], "wb")
                f.write(data)
                f.close()
                publishOTA(json.dumps({"ID": idMess}))

        if syncGW is not None:
            syncAll(
                sync_sensor=syncGW["Sensor"],
                sync_device=syncGW["Device"],
                sync_timeline=syncGW["Timeline"],
                sync_rule=syncGW["Rule"],
                sync_script=syncGW["Script"],
            )

        if action == "Reboot":
            publishOTA(json.dumps({"ID": idMess}))
            sleep(2)
            print("Reboot........")
            os.system("sudo reboot")

    def on_connect(clientMQTT, userdata, flags, rc):
        """
        :param clientMQTT:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        print("Connected with MQTT OTA")
        clientMQTT.subscribe(PackData.MacGateway + "_OTA_HOST")

    def on_message(clientMQTT, userdata, msg):
        """
        :param clientMQTT:
        :param userdata:
        :param msg:
        :return:
        """
        print(msg.topic, msg.payload)
        ChangeFile(json.loads(msg.payload))

    def on_disconnect(clientMQTT, userdata, rc):
        """
        :param clientMQTT:
        :param userdata:
        :param rc:
        :return:
        """
        print("disconnecting reason  " + str(rc))

    clientOTA.on_connect = on_connect
    clientOTA.on_message = on_message
    clientOTA.on_disconnect = on_disconnect
    clientOTA.username_pw_set(USER_SERVER, PASS_SERVER)
    try:
        clientOTA.connect(IP_SERVER, PORT_SERVER, 60)
    except:
        print("Cannot Connected MQTT!")
    clientOTA.loop_start()


def publishOTA(message):
    """
    :param message:
    :return:
    """
    print(message)
    try:
        clientOTA.publish(PackData.MacGateway + "_OTA_GW", message)
    except:
        print("publish mqtt Server error!")


def publishBLE(message):
    """
    :param message:
    :return:
    """
    print("BLE mesage:", message)
    try:
        ble.publish("RD_CONTROL", json.dumps(message))
        logger.info(f"Data Send To Topic RD_CONTROL {json.dumps(message)}")
    except:
        print("publish mqtt BLE error!")
        logger.error("publish mqtt BLE error!")


def publishMqtt(message):
    """
    :param message:
    :return:
    """
    print(message)
    try:
        client.publish(PackData.MacGateway + "gateway", message)
        logger.info(
            f"Data Send To Server -> Topic: {PackData.MacGateway}gateway -> Message: {message}"
        )
    except:
        print("publish mqtt Server error!")
        logger.error("publish mqtt Server error!")


def sync():
    """
    :return:
    """
    allSensor = SQL().getMultiSensor()
    allDevice = SQL().getMultiDevice()
    allTimeline = SQL().getMultiTimelineSql()
    allRule = SQL().getMultiRulesSql()
    allScript = SQL().getMultiScript()
    message = PackData.PackGateway(
        allSensor=allSensor,
        allDevice=allDevice,
        allTimeline=allTimeline,
        allRule=allRule,
        allScript=allScript,
    )
    valSensor = []
    for x in allSensor:
        s = PackData.PackValueSensor(x[13], x[4], x[5], x[6])
        valSensor.append(s)
    message1 = PackData.PackSensor(random.randint(20000000, 300000000), valSensor)
    valControl = []
    for x in allDevice:
        if x[5] == 1:
            s = PackData.PackValueControl(x[2], PackData.TypeDevice["Relay"], x[7])
        else:
            s = PackData.PackValueControl(
                x[2], PackData.TypeDevice["Relay"], x[7], x[8], x[9]
            )
        valControl.append(s)
    message2 = PackData.PackControl(random.randint(20000000, 300000000), valControl)
    publishMqtt(message)
    sleep(1)
    publishMqtt(message2)


def PackTimeline(idTimeline):
    """
    :param idTimeline:
    :return:
    """
    condition = SQL().getConditionTimeline(idTimeline)[0]
    inputCondition = PackData.PackConditionTimeline(
        condition[2],
        [
            condition[3],
            condition[4],
            condition[5],
            condition[6],
            condition[7],
            condition[8],
            condition[9],
        ],
    )
    execute = []
    action = SQL().getActionTimeline(idTimeline)
    for x in action:
        singleDevice = SQL().getSingleDeviceAtID(x[2])[0]
        if singleDevice[5] == 1:
            data = PackData.PackActionTimeline(
                id=singleDevice[2], type=PackData.TypeDevice["Relay"], pull=x[3]
            )
        else:
            data = PackData.PackActionTimeline(
                id=singleDevice[2],
                type=PackData.TypeDevice["Led"],
                pull=x[3],
                dim=x[4],
                cct=x[5],
            )
        execute.append(data)

    singleTimeline = SQL().getSingleTimelineSql(idTimeline)[0]
    packageTimeline = PackData.PackRule(
        id=singleTimeline[0],
        type=PackData.TypeRule["Schedule"],
        name=singleTimeline[1],
        active=singleTimeline[2],
        action=PackData.TypeAction["Addition"],
        input=inputCondition,
        exe=execute,
    )
    return packageTimeline


def PackRule(idRule):
    """
    :param idRule:
    :return:
    """
    condition = SQL().getConditionRules(idRule)
    inputCondition = []
    for x in condition:
        objectSensor = SQL().getSingleSensorAtID(x[2])[0]
        inputCondition.append(
            PackData.PackConditionRule(
                id=objectSensor[13], type=objectSensor[4], value=x[4], equal=x[3]
            )
        )
    condition2 = SQL().getConditionRules2(idRule)[0]
    inputCondition = {
        "Schedule": {
            "TimeStart": condition2[2],
            "TimeStop": condition2[3],
            "TimeUpdate": condition2[4],
        },
        "Loop": {
            "Monday": condition2[5],
            "Tuesday": condition2[6],
            "Wednesday": condition2[7],
            "Thursday": condition2[8],
            "Friday": condition2[9],
            "Saturday": condition2[10],
            "Sunday": condition2[11],
        },
        "Condition": {"Compare": inputCondition, "Logic": condition2[12]},
    }

    action = SQL().getActionRules(idRule)
    execute = []
    for x in action:
        isDevice = x[2]
        if isDevice == 1:
            objectDevice = SQL().getSingleDeviceAtID(x[3])[0]
            if objectDevice[5] == 1:
                data = PackData.PackActionRule(
                    id=objectDevice[2],
                    type=PackData.TypeDevice["Relay"],
                    pull=x[4],
                    delay=x[7],
                    during=x[8],
                )
            else:
                data = PackData.PackActionRule(
                    id=objectDevice[2],
                    type=PackData.TypeDevice["Led"],
                    pull=x[4],
                    dim=x[5],
                    cct=x[6],
                    delay=x[7],
                    during=x[8],
                )
        else:
            data = PackData.PackActionRule(
                id=x[3], type=PackData.TypeDevice["Script"], pull=x[4]
            )
        execute.append(data)

    rule = SQL().getSingleRulesSql(idRule)[0]
    active = rule[2]
    name = rule[1]
    packageRule = PackData.PackRule(
        id=idRule,
        type=PackData.TypeRule["Rule"],
        action=PackData.TypeAction["Addition"],
        name=name,
        active=active,
        input=inputCondition,
        exe=execute,
    )
    return packageRule


def PackScript(idScript):
    """
    :param idScript:
    :return:
    """
    action = SQL().getActionScript(idScript)
    execute = []
    for x in action:
        objectDevice = SQL().getSingleDeviceAtID(x[2])[0]
        if objectDevice[5] == 1:
            data = PackData.PackActionRule(
                id=objectDevice[2],
                type=PackData.TypeDevice["Relay"],
                pull=x[3],
                delay=x[6],
                during=x[7],
            )
        else:
            data = PackData.PackActionRule(
                id=objectDevice[2],
                type=PackData.TypeDevice["Led"],
                pull=x[3],
                dim=x[4],
                cct=x[5],
                delay=x[6],
                during=x[7],
            )
        execute.append(data)

    rule = SQL().getSingleScript(idScript)[0]
    packageScript = PackData.PackRule(
        id=idScript,
        type=PackData.TypeRule["Script"],
        action=PackData.TypeAction["Addition"],
        name=rule[1],
        active=rule[2],
        exe=execute,
    )
    return packageScript


def PackDevice(idDevice):
    """
    :param idDevice:
    :return:
    """
    objectDevice = SQL().getSingleDeviceAtID(idDevice)[0]
    if objectDevice[5] == 1:
        typeDevice = PackData.TypeDevice["Relay"]
        pin = objectDevice[6]
    else:
        typeDevice = PackData.TypeDevice["Led"]
        pin = 0
    packageDevice = PackData.PackValueDevice(
        mac=objectDevice[2],
        name=objectDevice[1],
        type=typeDevice,
        pin=pin,
        action=PackData.TypeAction["Addition"],
    )
    return packageDevice


def PackSensor(idSensor):
    """
    :param idSensor:
    :return:
    """
    objectSensor = SQL().getSingleSensorAtID(idSensor)[0]
    packageSensor = PackData.PackValueDevice(
        mac=objectSensor[13],
        type=PackData.TypeDevice["Sensor"],
        typesensor=objectSensor[4],
        name=objectSensor[1],
        value=objectSensor[5],
        battery=objectSensor[6],
        max=objectSensor[8],
        min=objectSensor[7],
        par_a=objectSensor[9],
        par_b=objectSensor[10],
        par_c=objectSensor[11],
        delay=objectSensor[12],
        action=PackData.TypeAction["Addition"],
    )
    return packageSensor


def syncAll(sync_sensor=0, sync_device=0, sync_timeline=0, sync_rule=0, sync_script=0):
    """ "
    :return:
    """
    print("Sync All")
    if sync_device == 1:
        valueDevice = []
        allDevice = SQL().getMultiDevice()
        for x in allDevice:
            value = PackDevice(x[0])
            valueDevice.append(value)
        idMessage = random.randint(20000000, 300000000)
        packageDevice = PackData.PackDevice(
            idMessage=idMessage, valueDevice=valueDevice
        )
        publishMqtt(packageDevice)
        sleep(1)

    if sync_sensor == 1:
        valueSensor = []
        allSensor = SQL().getMultiSensor()
        for x in allSensor:
            value = PackSensor(x[0])
            valueSensor.append(value)
        idMessage = random.randint(20000000, 300000000)
        packageSensor = PackData.PackDevice(
            idMessage=idMessage, valueDevice=valueSensor
        )
        publishMqtt(packageSensor)
        sleep(1)

    if sync_timeline == 1:
        valueTimeline = []
        allTimeline = SQL().getMultiTimelineSql()
        for x in allTimeline:
            value = PackTimeline(x[0])
            valueTimeline.append(value)
        idMessage = random.randint(20000000, 300000000)
        packageTimeline = PackData.PackTRS(idMessage=idMessage, trs=valueTimeline)
        publishMqtt(packageTimeline)
        sleep(1)

    if sync_rule == 1:
        valueRule = []
        allRule = SQL().getMultiRulesSql()
        for x in allRule:
            value = PackRule(x[0])
            valueRule.append(value)
        idMessage = random.randint(20000000, 300000000)
        packageRule = PackData.PackTRS(idMessage=idMessage, trs=valueRule)
        publishMqtt(packageRule)
        sleep(1)

    if sync_script == 1:
        allScript = SQL().getMultiScript()
        valueScript = []
        for x in allScript:
            value = PackScript(x[0])
            valueScript.append(value)
        idMessage = random.randint(20000000, 300000000)
        packageScript = PackData.PackTRS(idMessage=idMessage, trs=valueScript)
        publishMqtt(packageScript)
        sleep(1)
    sync()


if __name__ == "__main__":
    print("START PROGRAMMING ...")
    logger.info("START PROGRAMMING ...")
    settings = QSettings("Farm", "Info")
    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon("Image/logo2.png"))
    engine = QQmlApplicationEngine()
    engine.load(os.fspath(Path(__file__).resolve().parent / "main.qml"))
    sql = SQL()
    if not engine.rootObjects():
        sys.exit(-1)
    device = Device()
    sensor = Sensor()
    timeline = Timeline()
    rules = Rules()
    script = Script()
    GPIOPI.configGPIO()
    cloudMessage = CloudMessage()
    gatewayMessage = GatewayMessage()
    bleMessage = BLEMessage()
    device.showAllDevice()
    sensor.showAllSensor()
    rules.showAllRules()
    timeline.showAllTimeline()
    script.showAllScript()
    configureThread()
    configureMQTT_MAC()
    configureTimer()
    publishMqtt("Start")
    sys.exit(app.exec_())
