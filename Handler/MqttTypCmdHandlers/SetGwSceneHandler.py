import uuid
import threading
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
from Database.Db import Db
import logging
import json
import Constants.Constant as Const
import sqlite3


def sql_insert(cmd):
    con = sqlite3.connect('rd.sqlite')
    cur = con.cursor()

    # Insert a row of data
    cur.execute(cmd)
    con.commit()
    con.close()


def sql_select(cmd):
    con = sqlite3.connect('rd.sqlite')
    cur = con.cursor()

    # Insert a row of data
    cur.execute(cmd)
    con.commit()
    con.close()
    return cur.fetchall()


def sql_delete(cmd):
    con = sqlite3.connect('rd.sqlite')
    cur = con.cursor()

    # Insert a row of data
    cur.execute(cmd)
    con.commit()
    con.close()


class SetGwSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")
        mqttReceiveCommandResponse = {
            "RQI": rqi,
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC,
                       json.dumps(mqttReceiveCommandResponse))

        rel = db.Services.GatewayEventTriggerService.FindGatewayEventTriggerById(
            data.get("ID"))
        event = rel.fetchone()

        if event is None:
            self.__save_new_scene_to_db(data)

        if event is not None:
            self.__remove_all_event_data(data.get("ID"))
            self.__save_new_scene_to_db(data)

    def __save_new_scene_to_db(self, data):
        db = Db()
        db.Services.GatewayEventTriggerService.InsertGatewayEventTrigger(
            {
                "EventTriggerId": data.get("ID"),
                "ScriptType": data.get("script_type"),
                "IsEnable": True,
                "ScheduleRaw": data.get("input_condition").get("schedule")
            }
        )
        self.__save_input_condition_to_db(data)
        self.__save_output_action_to_db(data)

    def __save_input_condition_to_db(self, data):
        db = Db()
        devices_input_condition = data.get(
            "input_condition").get("condition", [])
        if not devices_input_condition:
            return

        devices_mapping_input_insert = []
        devices_setup_input_insert = []

        for device_input_condition in devices_input_condition:
            device_mapping_input_insert = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_input_condition.get("Device"),
            }

            device_setup_input_insert = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_input_condition.get("Device"),
                "PropertyId": device_input_condition.get("condition").get("attribute"),
                "PropertyValue": device_input_condition.get("condition").get("value"),
                "Operation": device_input_condition.get("condition").get("operation")
            }
            devices_setup_input_insert.append(device_setup_input_insert)
            devices_mapping_input_insert.append(device_mapping_input_insert)

        db.Services.EventTriggerInputDeviceMappingService.InsertManyEventTriggerInputDeviceMapping(
            devices_mapping_input_insert)
        db.Services.EventTriggerInputDeviceSetupValueService.InsertManyEventTriggerInputDeviceSetupValue(
            devices_setup_input_insert
        )

    def __save_output_action_to_db(self, data):
        db = Db()

        relays_output_action = data.get("execute")
        relay_1 = relays_output_action.get('Relay_1')
        relay_2 = relays_output_action.get('Relay_2')
        relay_3 = relays_output_action.get('Relay_3')
        relay_4 = relays_output_action.get('Relay_4')

        if relay_1 is not None:
            relay_output_setup_value = {
                "EventTriggerId": data.get("ID"),
                "Relay": "Relay_1",
                "Value": relay_1
            }
            db.Services.GatewayEventTriggerOutputRelayService.InsertEventTriggerOutputRelay(
                relay_output_setup_value
            )

        if relay_2 is not None:
            relay_output_setup_value = {
                "EventTriggerId": data.get("ID"),
                "Relay": "Relay_2",
                "Value": relay_2
            }
            db.Services.GatewayEventTriggerOutputRelayService.InsertEventTriggerOutputRelay(
                relay_output_setup_value
            )

        if relay_3 is not None:
            relay_output_setup_value = {
                "EventTriggerId": data.get("ID"),
                "Relay": "Relay_3",
                "Value": relay_3
            }
            db.Services.GatewayEventTriggerOutputRelayService.InsertEventTriggerOutputRelay(
                relay_output_setup_value
            )

        if relay_4 is not None:
            relay_output_setup_value = {
                "EventTriggerId": data.get("ID"),
                "Relay": "Relay_4",
                "Value": relay_4
            }
            db.Services.GatewayEventTriggerOutputRelayService.InsertEventTriggerOutputRelay(
                relay_output_setup_value
            )

    def __remove_all_event_data(self, event: int):
        db = Db()
        db.Services.EventTriggerInputDeviceSetupValueService.RemoveEventTriggerInputDeviceSetupValueByCondition(
            db.Table.EventTriggerInputDeviceSetupValueTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerInputDeviceMappingService.RemoveEventTriggerInputDeviceMappingByCondition(
            db.Table.EventTriggerInputDeviceMappingTable.c.EventTriggerId == event
        )
        db.Services.GatewayEventTriggerOutputRelayService.RemoveEventTriggerOutputRelayByCondition(
            db.Table.GatewayEventTriggerOutputRelayTable.c.EventTriggerId == event
        )
        db.Services.GatewayEventTriggerService.RemoveGatewayEventTriggerByCondition(
            db.Table.GatewayEventTriggerTable.c.EventTriggerId == event
        )
