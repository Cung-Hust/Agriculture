import json
import logging
import Constants.Constant as Const
from Constracts.IHandler import IHandler
from Constracts.ITransport import ITransport


class DeviceDataHandler(IHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport, uart: ITransport):
        self.__logger = log
        self.__mqtt = mqtt
        self.__uart = uart

    def handler(self, data):
        data = data.hex()
        print(f"data from uart:{data}")
        code = data[:8]
        # print(code)
        try:
            switcher = {
                Const.OPCODE_TEMP_HUMI_INFO: self.__handler_temp_humi_info,
                Const.OPCODE_LIGHT_INFO: self.__handler_light_info,
                Const.OPCODE_CO2_INFO: self.__handler_co2_info,
                Const.OPCODE_GND_HUMI_INFO: self.__handler_gnd_humi_info,
                Const.OPCODE_STATE_DEV_INFO: self.__handler_state_dev_info,
            }
            func = switcher.get(code)
            func(data)
            return True
        except:
            return False

    def __handler_temp_humi_info(self, data):
        dev_id = str(data[10:12]) + str(data[8:10])
        str_data_humi = str(data[20:22]) + \
            str(data[18:20])
        value_humi = int(str_data_humi, 16)/10

        str_data_temp = str(data[16:18]) + \
            str(data[14:16])
        value_temp = int(str_data_temp, 16)/100

        str_data_sign = str(data[12:14])
        if str_data_sign == "00":
            sign = -1
        else:
            sign = 1

        sensor_data = {}
        sensor_data[f'temperature_{dev_id}'] = value_temp * sign
        sensor_data[f'humidity_{dev_id}'] = value_humi
        print(f"data:{sensor_data}")
        self.__mqtt.send(
            Const.MQTT_RESPONSE_TOPIC, json.dumps(sensor_data))

    def __handler_light_info(self, data):
        str_data_light = str(data[14:16]) + \
            str(data[12:14])
        value_light = int(str_data_light, 16)

        sensor_data = {}
        sensor_data['light'] = value_light
        print(f"data:{sensor_data}")
        self.__mqtt.send(
            Const.MQTT_RESPONSE_TOPIC, json.dumps(sensor_data))

    def __handler_co2_info(self, data):
        str_data_co2 = str(data[14:16]) + \
            str(data[12:14])
        value_co2 = int(str_data_co2, 16)

        str_data_tvoc = str(data[18:20]) + \
            str(data[16:18])
        value_tvoc = int(str_data_tvoc, 16)

        sensor_data = {}
        sensor_data['co2'] = value_co2
        sensor_data['tvoc'] = value_tvoc
        print(f"data:{sensor_data}")
        self.__mqtt.send(
            Const.MQTT_RESPONSE_TOPIC, json.dumps(sensor_data))

    def __handler_gnd_humi_info(self, data):
        str_data_gnd_humi = str(data[12:14])
        value_gnd_humi = int(str_data_gnd_humi, 16)

        sensor_data = {}
        sensor_data['gnd humidity'] = value_gnd_humi
        print(f"data:{sensor_data}")
        self.__mqtt.send(
            Const.MQTT_RESPONSE_TOPIC, json.dumps(sensor_data))

    def __handler_state_dev_info(self, data):
        str_data_state_dev = str(data[12:14])
        value_state_dev = int(str_data_state_dev, 16)

        state_data = {}
        state_data['state device'] = value_state_dev
        print(f"data:{state_data}")
        self.__mqtt.send(
            Const.MQTT_RESPONSE_TOPIC, json.dumps(state_data))
