import paho.mqtt.client as mqtt
from dsmr_parser import obis_references
from dsmr_parser.objects import Telegram

from p1reader.sinks.data_sink import DataSink, DataSinkConfig


class MQTTSinkConfig(DataSinkConfig):
    host: str
    port: int = 1883
    qos: int = 1

    @property
    def output_stream(self) -> DataSink:
        return MQTTSink(host=self.host, port=self.port, qos=self.qos)


class MQTTSink(DataSink):
    def __init__(self, host: str, port: int, qos: int) -> None:
        self._mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._mqtt.connect(host=host, port=port)
        self._qos = qos
        self._mqtt.loop_start()

    def process_telegram(self, telegram: Telegram) -> None:
        device_id = bytearray.fromhex(
            telegram[obis_references.BELGIUM_EQUIPMENT_IDENTIFIER].value
        ).decode()
        self._mqtt.publish(f"telegram/{device_id}", telegram.to_json(), qos=self._qos)
