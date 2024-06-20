from confluent_kafka import Producer, Consumer, KafkaException
import json

class KafkaService:
    def __init__(self, brokers):
        self.producer = Producer({'bootstrap.servers': brokers})
        self.consumer = Consumer({
            'bootstrap.servers': brokers,
            'group.id': 'backtest_group',
            'auto.offset.reset': 'earliest'
        })

    def produce(self, topic, message):
        self.producer.produce(topic, key=None, value=json.dumps(message))
        self.producer.flush()

    def consume(self, topic, callback):
        self.consumer.subscribe([topic])
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            callback(json.loads(msg.value()))

kafka_service = KafkaService(brokers='localhost:9092')
