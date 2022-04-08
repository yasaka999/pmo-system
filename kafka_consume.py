import json

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "zabbix", bootstrap_servers=["192.168.5.5:9092"], value_deserializer=json.loads
)
for msg in consumer:
    recv = "%s:%d:%d: key=%s value=%s" % (
        msg.topic,
        msg.partition,
        msg.offset,
        msg.key,
        msg.value,
    )
    print(recv)
