import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import threading
import time


class SetSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        print("Hello world")
        r = {}
        db = Db()

        mqttReceiveCommandResponse = {
            "RQI": data.get("RQI"),
            "Rsp": 0
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC,
                       json.dumps(mqttReceiveCommandResponse))

        rel = db.Services.EventTriggerService.FindEventTriggerById(
            data.get("ID"))
        event = rel.fetchone()

        if event is None:
            self.__save_new_scene_to_db(data)

        if event is not None:
            self.__get_different(data)
            self.__remove_all_event_data(data.get("ID"))
            self.__save_new_scene_to_db(data)
            # self.__update_scene_to_db(data)

        devices_output_action = data.get("execute").get("device_action", [])
        groups_output_action = data.get("execute").get("group_action", [])
        group_devices_mapping_action = []

        # added by cungdd 18/10
        cmd_send_to_devivce = {
            "TYPCMD": "SetDevScene",
            "ID": data.get("ID"),
            "script_type": data.get("script_type"),
            "input_condition": data.get("input_condition"),
            # "execute": {}
        }
        device_output = []
        for group_output_action in groups_output_action:
            action = group_output_action.get("action")
            group_devices_mapping_action = []
            rel = db.Services.GroupDeviceMappingService.FindGroupDeviceMappingByCondition(
                db.Table.GroupDeviceMappingTable.c.GroupId == group_output_action.get(
                    "GroupId")
            )

            if action["Type"] == 0:
                for r in rel:
                    group_devices_mapping_action.append(r["DeviceAddress"])
            if action["Type"] == 1:
                for r in rel:
                    if r["Number"] % 2 == 1:
                        group_devices_mapping_action.append(r["DeviceAddress"])
            if action["Type"] == 2:
                for r in rel:
                    if r["Number"] % 2 == 0:
                        group_devices_mapping_action.append(r["DeviceAddress"])
            # device_output = []
            for d in group_devices_mapping_action:
                if group_output_action.get("action").get("DIM") is not None:
                    cmd = {
                        "Device": d,
                        "Relay": group_output_action.get("action").get("Relay"),
                        "DIM": group_output_action.get("action").get("DIM")
                    }
                else:
                    cmd = {
                        "Device": d,
                        "Relay": group_output_action.get("action").get("Relay")
                    }
                device_output.append(cmd)
        # end

        for d in devices_output_action:
            if d.get("action").get("DIM") is not None:
                cmd = {
                    "Device": d.get("Device"),
                    "Relay": d.get("action").get("Relay"),
                    "DIM": d.get("action").get("DIM")
                }
            else:
                cmd = {
                    "Device": d.get("Device"),
                    "Relay": d.get("action").get("Relay")
                }

            device_output.append(cmd)

        all_devs = cmd_send_to_devivce.get('execute', [])
        for each_dev in all_devs:
            cmd_set_scene = [{
                "TYPCMD": "SetDevScene",
                "ID": data.get("ID"),
                "script_type": data.get("script_type"),
                "input_condition": data.get("input_condition"),
                "execute": each_dev
            }]
            print(cmd_set_scene)
            self.addConfigQueue(cmd_set_scene)

        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()

    def __get_different(self, data):
        r = {}
        db = Db()
        old_devices_mapping_action = []
        rel = db.Services.EventTriggerOutputDeviceMappingService.FindEventTriggerOutputDeviceMappingByCondition(
            db.Table.EventTriggerOutputDeviceMappingTable.c.EventTriggerId == data.get(
                "ID")
        )
        for r in rel:
            old_devices_mapping_action.append(r["DeviceAddress"])

        devices_output_action = data.get("execute").get("device_action", [])
        groups_output_action = data.get("execute").get("group_action", [])
        group_devices_mapping_action = []

        # added by cungdd 18/10
        new_devices_mapping_action = []
        cmd_send_to_devivce = {
            "TYPCMD": "SetDevScene",
            "ID": data.get("ID"),
            "script_type": data.get("script_type"),
            "input_condition": data.get("input_condition"),
            # "execute": {}
        }
        device_output = []
        for group_output_action in groups_output_action:
            action = group_output_action.get("action")
            group_devices_mapping_action = []
            rel = db.Services.GroupDeviceMappingService.FindGroupDeviceMappingByCondition(
                db.Table.GroupDeviceMappingTable.c.GroupId == group_output_action.get(
                    "GroupId")
            )

            if action["Type"] == 0:
                for r in rel:
                    group_devices_mapping_action.append(r["DeviceAddress"])
            if action["Type"] == 1:
                for r in rel:
                    if r["Number"] % 2 == 1:
                        group_devices_mapping_action.append(r["DeviceAddress"])
            if action["Type"] == 2:
                for r in rel:
                    if r["Number"] % 2 == 0:
                        group_devices_mapping_action.append(r["DeviceAddress"])
            # device_output = []
            for d in group_devices_mapping_action:
                if group_output_action.get("action").get("DIM") is not None:
                    cmd = {
                        "Device": d,
                        "Relay": group_output_action.get("action").get("Relay"),
                        "DIM": group_output_action.get("action").get("DIM")
                    }
                else:
                    cmd = {
                        "Device": d,
                        "Relay": group_output_action.get("action").get("Relay")
                    }
                device_output.append(cmd)
                new_devices_mapping_action.append(d)
        # end

        for d in devices_output_action:
            if d.get("action").get("DIM") is not None:
                cmd = {
                    "Device": d.get("Device"),
                    "Relay": d.get("action").get("Relay"),
                    "DIM": d.get("action").get("DIM")
                }
            else:
                cmd = {
                    "Device": d.get("Device"),
                    "Relay": d.get("action").get("Relay")
                }

            device_output.append(cmd)

            new_devices_mapping_action.append(d.get("Device"))

        set_difference = set(old_devices_mapping_action) - \
            set(new_devices_mapping_action)
        list_difference = list(set_difference)

        print(list_difference)

        for d in list_difference:
            cmd_send_del_dev_to_device = {
                "TYPCMD": "DelDeviceInScene",
                "ID": data.get("ID"),
                "Device": d
            }
            self.addConfigQueue(cmd_send_del_dev_to_device)

        cmd_send_to_devivce["execute"] = device_output
        self.addConfigQueue(cmd_send_to_devivce)

        self.send_ending_cmd(self.addConfigQueue)
        self.waiting_for_handler_cmd()

    def __save_new_scene_to_db(self, data):
        db = Db()
        db.Services.EventTriggerService.InsertEventTrigger(
            {
                "EventTriggerId": data.get("ID"),
                "ScriptType": data.get("script_type"),
                "IsEnable": True,
                "ScheduleRaw": data.get("input_condition").get("schedule")
            }
        )
        self.__save_input_condition_to_db(data)
        self.__save_output_action_to_db(data)

    # added by cungdd
    def __update_scene_to_db(self, data):
        db = Db()
        db.Services.EventTriggerService.UpdateEventTriggerCondition(
            db.Table.EventTriggerTable.c.EventTriggerId == data.get("ID"),
            {
                "EventTriggerId": data.get("ID"),
                "ScriptType": data.get("script_type"),
                "IsEnable": True,
                "ScheduleRaw": data.get("input_condition").get("schedule")
            }
        )
        self.__update_input_condition_to_db(data)
        self.__update_output_action_to_db(data)
    # end

    def __save_input_condition_to_db(self, data):
        db = Db()
        devices_input_condition = data.get(
            "input_condition").get("device_condition", [])
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

    def __update_input_condition_to_db(self, data):
        db = Db()
        devices_input_condition = data.get(
            "input_condition").get("device_condition", [])
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

        db.Services.EventTriggerInputDeviceMappingService.UpdateEventTriggerInputDeviceMappingByCondition(
            db.Table.EventTriggerInputDeviceMappingTable.c.EventTriggerId == data.get('ID'), devices_mapping_input_insert)
        db.Services.EventTriggerInputDeviceSetupValueService.UpdateEventTriggerInputDeviceSetupValueByCondition(
            db.Table.EventTriggerInputDeviceMappingTable.c.EventTriggerId == data.get(
                'ID'), devices_setup_input_insert
        )

    def __save_output_action_to_db(self, data):
        db = Db()

        devices_output_action = data.get("execute").get("device_action", [])
        devices_output_mapping = []
        devices_output_setup_value = []
        devices_success_list = []

        groups_output_action = data.get("execute").get("group_action", [])
        groups_output_mapping = []
        groups_output_setup_value = []
        groups_success_list = []

        for device_output_action in devices_output_action:
            action = device_output_action.get("action")
            device_output_relay_setup_value = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_output_action.get("Device"),
                "PropertyId": Const.PROPERTY_RELAY_ID,
                "PropertyValue": action.get("Relay")
            }
            if action.get("DIM") is not None:
                device_output_dim_setup_value = {
                    "EventTriggerId": data.get("ID"),
                    "DeviceAddress": device_output_action.get("Device"),
                    "PropertyId": Const.PROPERTY_DIM_ID,
                    "PropertyValue": action.get("DIM")
                }
                devices_output_setup_value.append(
                    device_output_dim_setup_value)

            else:
                device_output_dim_setup_value = {}
            device_output_mapping = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_output_action.get("Device"),
                "IsEnable": True
            }
            devices_output_setup_value.append(device_output_relay_setup_value)
            devices_output_mapping.append(device_output_mapping)
            devices_success_list.append(device_output_action.get("Device"))

        for group_output_action in groups_output_action:
            action = group_output_action.get("action")
            group_output_relay_setup_value = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "PropertyId": Const.PROPERTY_RELAY_ID,
                "PropertyValue": action.get("Relay")
            }
            if action.get("DIM") is not None:
                group_output_dim_setup_value = {
                    "EventTriggerId": data.get("ID"),
                    "GroupId": group_output_action.get("GroupId"),
                    "PropertyId": Const.PROPERTY_DIM_ID,
                    "PropertyValue": action.get("DIM")
                }
                groups_output_setup_value.append(group_output_dim_setup_value)

            group_output_type_setup_value = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "PropertyId": Const.PROPERTY_TYPE_ID,
                "PropertyValue": action.get("Type")
            }
            group_output_mapping = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "IsEnable": True
            }

            # added by cungdd

            group_devices_mapping_action = []
            rel = db.Services.GroupDeviceMappingService.FindGroupDeviceMappingByCondition(
                db.Table.GroupDeviceMappingTable.c.GroupId == group_output_action.get(
                    "GroupId")
            )
            if action["Type"] == 0:
                for r in rel:
                    group_devices_mapping_action.append(r["DeviceAddress"])
            if action["Type"] == 1:
                for r in rel:
                    if r["Number"] % 2 == 1:
                        group_devices_mapping_action.append(r["DeviceAddress"])
            if action["Type"] == 2:
                for r in rel:
                    if r["Number"] % 2 == 0:
                        group_devices_mapping_action.append(r["DeviceAddress"])

            for d in group_devices_mapping_action:
                device_output_relay_setup_value = {
                    "EventTriggerId": data.get("ID"),
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_RELAY_ID,
                    "PropertyValue": action.get("Relay")
                }
                if action.get("DIM") is not None:
                    device_output_dim_setup_value = {
                        "EventTriggerId": data.get("ID"),
                        "DeviceAddress": d,
                        "PropertyId": Const.PROPERTY_DIM_ID,
                        "PropertyValue": action.get("DIM")
                    }
                    devices_output_setup_value.append(
                        device_output_dim_setup_value)

                device_output_mapping = {
                    "EventTriggerId": data.get("ID"),
                    "DeviceAddress": d,
                    "IsEnable": True
                }
                devices_output_setup_value.append(
                    device_output_relay_setup_value)
                devices_output_mapping.append(device_output_mapping)

            # end

            groups_output_setup_value.append(group_output_relay_setup_value)
            groups_output_setup_value.append(group_output_type_setup_value)

            groups_output_mapping.append(group_output_mapping)
            groups_success_list.append(group_output_action.get("GroupId"))

        if devices_output_mapping:
            db.Services.EventTriggerOutputDeviceMappingService.InsertManyEventTriggerOutputDeviceMapping(
                devices_output_mapping
            )
        if devices_output_setup_value:
            db.Services.EventTriggerOutputDeviceSetupValueService.InsertManyEventTriggerOutputDeviceSetupValue(
                devices_output_setup_value
            )
        if groups_output_mapping:
            db.Services.EventTriggerOutputGroupMappingService.InsertManyEventTriggerOutputGroupMapping(
                groups_output_mapping
            )
        if groups_output_setup_value:
            db.Services.EventTriggerOutputGroupSetupValueService.InsertEventTriggerOutputGroupSetupValue(
                groups_output_setup_value
            )

    def __update_output_action_to_db(self, data):
        db = Db()

        devices_output_action = data.get("execute").get("device_action", [])
        devices_output_mapping = []
        devices_output_setup_value = []
        devices_success_list = []

        groups_output_action = data.get("execute").get("group_action", [])
        groups_output_mapping = []
        groups_output_setup_value = []
        groups_success_list = []

        # device_output_dim_setup_value = {}
        # group_output_dim_setup_value = {}

        for device_output_action in devices_output_action:
            action = device_output_action.get("action")
            device_output_relay_setup_value = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_output_action.get("Device"),
                "PropertyId": Const.PROPERTY_RELAY_ID,
                "PropertyValue": action.get("Relay")
            }
            if action.get("DIM") is not None:
                device_output_dim_setup_value = {
                    "EventTriggerId": data.get("ID"),
                    "DeviceAddress": device_output_action.get("Device"),
                    "PropertyId": Const.PROPERTY_DIM_ID,
                    "PropertyValue": action.get("DIM")
                }
                devices_output_setup_value.append(
                    device_output_dim_setup_value)

            else:
                device_output_dim_setup_value = {}
            device_output_mapping = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_output_action.get("Device"),
                "IsEnable": True,
                "Success": False
            }
            devices_output_setup_value.append(device_output_relay_setup_value)
            devices_output_mapping.append(device_output_mapping)
            devices_success_list.append(device_output_action.get("Device"))

        for group_output_action in groups_output_action:
            action = group_output_action.get("action")
            group_output_relay_setup_value = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "PropertyId": Const.PROPERTY_RELAY_ID,
                "PropertyValue": action.get("Relay")
            }
            if action.get("DIM") is not None:
                group_output_dim_setup_value = {
                    "EventTriggerId": data.get("ID"),
                    "GroupId": group_output_action.get("GroupId"),
                    "PropertyId": Const.PROPERTY_DIM_ID,
                    "PropertyValue": action.get("DIM")
                }
                groups_output_setup_value.append(group_output_dim_setup_value)

            group_output_type_setup_value = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "PropertyId": Const.PROPERTY_TYPE_ID,
                "PropertyValue": action.get("Type")
            }
            group_output_mapping = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "IsEnable": True
            }

            # added by cungdd

            group_devices_mapping_action = []
            rel = db.Services.GroupDeviceMappingService.FindGroupDeviceMappingByCondition(
                db.Table.GroupDeviceMappingTable.c.GroupId == group_output_action.get(
                    "GroupId")
            )
            if action["Type"] == 0:
                for r in rel:
                    group_devices_mapping_action.append(r["DeviceAddress"])
            if action["Type"] == 1:
                for r in rel:
                    if r["Number"] % 2 == 1:
                        group_devices_mapping_action.append(r["DeviceAddress"])
            if action["Type"] == 2:
                for r in rel:
                    if r["Number"] % 2 == 0:
                        group_devices_mapping_action.append(r["DeviceAddress"])

            for d in group_devices_mapping_action:
                device_output_relay_setup_value = {
                    "EventTriggerId": data.get("ID"),
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_RELAY_ID,
                    "PropertyValue": action.get("Relay")
                }
                if action.get("DIM") is not None:
                    device_output_dim_setup_value = {
                        "EventTriggerId": data.get("ID"),
                        "DeviceAddress": d,
                        "PropertyId": Const.PROPERTY_DIM_ID,
                        "PropertyValue": action.get("DIM")
                    }
                    devices_output_setup_value.append(
                        device_output_dim_setup_value)

                device_output_mapping = {
                    "EventTriggerId": data.get("ID"),
                    "DeviceAddress": d,
                    "IsEnable": True,
                    "Success": False
                }
                devices_output_setup_value.append(
                    device_output_relay_setup_value)
                devices_output_mapping.append(device_output_mapping)
                # #####################################
                print(devices_output_mapping)

            # end

            groups_output_setup_value.append(group_output_relay_setup_value)
            groups_output_setup_value.append(group_output_type_setup_value)

            groups_output_mapping.append(group_output_mapping)
            groups_success_list.append(group_output_action.get("GroupId"))

        if devices_output_mapping:
            db.Services.EventTriggerOutputDeviceMappingService.UpdateEventTriggerOutputDeviceMappingByCondition(
                db.Table.EventTriggerOutputDeviceMappingTable.c.EventTriggerId == data.get(
                    'ID'), devices_output_mapping
            )
        if devices_output_setup_value:
            db.Services.EventTriggerOutputDeviceSetupValueService.UpdateEventTriggerOutputDeviceSetupValueByCondition(
                db.Table.EventTriggerOutputDeviceSetupValueTable.c.EventTriggerId == data.get(
                    'ID'), devices_output_setup_value
            )
        if groups_output_mapping:
            db.Services.EventTriggerOutputGroupMappingService.UpdateEventTriggerOutputGroupMappingByCondition(
                db.Table.EventTriggerOutputGroupMappingTable.c.EventTriggerId == data.get(
                    'ID'), groups_output_mapping
            )
        if groups_output_setup_value:
            db.Services.EventTriggerOutputGroupSetupValueService.UpdateEventTriggerOutputGroupSetupValueByCondition(
                db.Table.EventTriggerOutputGroupSetupValueTable.c.EventTriggerId == data.get(
                    'ID'), groups_output_setup_value
            )

    def __remove_all_event_data(self, event: int):
        db = Db()
        db.Services.EventTriggerInputDeviceSetupValueService.RemoveEventTriggerInputDeviceSetupValueByCondition(
            db.Table.EventTriggerInputDeviceSetupValueTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerInputDeviceMappingService.RemoveEventTriggerInputDeviceMappingByCondition(
            db.Table.EventTriggerInputDeviceMappingTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerOutputDeviceMappingService.RemoveEventTriggerOutputDeviceMappingByCondition(
            db.Table.EventTriggerOutputDeviceMappingTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerOutputDeviceSetupValueService.RemoveEventTriggerOutputDeviceSetupValueByCondition(
            db.Table.EventTriggerOutputDeviceSetupValueTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerOutputGroupMappingService.RemoveEventTriggerOutputGroupMappingByCondition(
            db.Table.EventTriggerOutputGroupMappingTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerOutputGroupSetupValueService.RemoveEventTriggerOutputGroupSetupValueByCondition(
            db.Table.EventTriggerOutputGroupSetupValueTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerService.RemoveEventTriggerByCondition(
            db.Table.EventTriggerTable.c.EventTriggerId == event
        )
