# -*- coding: utf-8 -*-
import json

import kafka

producer = kafka.KafkaProducer(
    bootstrap_servers="192.168.5.5:9092",
    value_serializer=lambda m: json.dumps(m).encode("utf-8"),
)
msg_a = {
    "sleep_time": 10,
    "db_config": {
        "database": "test_1",
        "host": "192.168.5.5",
        "user": "root",
        "password": "root",
    },
    "table": "msg",
    "msg": "zabbix_test",
}
msg = json.dumps(msg_a)
producer.send("zabbix", msg_a)
producer.close()
