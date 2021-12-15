import paho.mqtt.client as mqtt
import Constants.Constant as Const
import logging
import threading
from Constracts.ITransport import ITransport


class MqttConfig:
    host: str
    port: int
    qos: int
    keep_alive: int
    username: str
    password: str

    def __init__(self, host: str, port: int, qos: int, keep_alive: int, username: str, password: str):
        self.host = host
        self.port = port
        self.qos = qos
        self.keep_alive = keep_alive
        self.username = username
        self.password = password


class Mqtt(ITransport):
    __mqttConfig: MqttConfig
    __client: mqtt.Client
    __logger: logging.Logger
    __lock: threading.Lock

    def __init__(self, log: logging.Logger, config: MqttConfig):
        super().__init__()
        self.__logger = log
        self.__mqttConfig = config
        self.__client = mqtt.Client()
        self.__lock = threading.Lock()

    def __on_message(self, client, userdata, msg):
        message = msg.payload.decode("utf-8")
        topic = msg.topic
        item = {"topic": topic, "msg": message}
        self.receive_data_queue.put(item)
        return

    def __on_connect(self, client, userdata, flags, rc):
        self.__client.subscribe(
            topic=Const.MQTT_CONTROL_TOPIC, qos=self.__mqttConfig.qos)
        self.__client.subscribe(
            topic=Const.MQTT_RESPONSE_TOPIC, qos=self.__mqttConfig.qos)

    def send(self, destination, send_data):
        self.__client.publish(
            destination, payload=send_data, qos=Const.MQTT_QOS)

    def disconnect(self):
        self.__client.disconnect()

    def connect(self):
        self.__client.on_message = self.__on_message
        self.__client.on_connect = self.__on_connect
        self.__client.username_pw_set(
            username=self.__mqttConfig.username, password=self.__mqttConfig.password)
        try:
            self.__client.connect(self.__mqttConfig.host,
                                  self.__mqttConfig.port)
            self.__client.loop_start()
        except Exception as err:
            self.__logger.error(f"Exception in connect to mqtt: {err}")
            print(f"Exception in connect to mqtt: {err}")

    def reconnect(self):
        pass

    def receive(self):
        pass
