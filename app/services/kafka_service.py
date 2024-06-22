import logging
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
import json

class KafkaService:
    def __init__(self, brokers):
        self.brokers = brokers
        self.producer = Producer({'bootstrap.servers': brokers})
        self.consumer = Consumer({
            'bootstrap.servers': brokers,
            'group.id': 'backtest_group',
            'auto.offset.reset': 'earliest'
        })
        self.admin_client = AdminClient({'bootstrap.servers': brokers})

    def create_topic(self, topic):
        topic_metadata = self.admin_client.list_topics(timeout=10)
        if topic not in topic_metadata.topics:
            logging.info(f"Creating topic {topic}")
            new_topic = NewTopic(topic, num_partitions=1, replication_factor=1)
            fs = self.admin_client.create_topics([new_topic])
            for topic, f in fs.items():
                try:
                    f.result()  # The result itself is None
                    logging.info(f"Topic {topic} created successfully")
                except Exception as e:
                    logging.error(f"Failed to create topic {topic}: {str(e)}")
        else:
            logging.info(f"Topic {topic} already exists")

    def produce(self, topic, message):
        logging.info(f"Producing message to topic {topic}: {message}")
        self.producer.produce(topic, key=None, value=json.dumps(message))
        self.producer.flush()
        logging.info("Message produced successfully")

    def consume(self, topic, callback):
        self.create_topic(topic)
        self.consumer.subscribe([topic])
        logging.info(f"Subscribed to topic {topic}")
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    logging.debug("No message received")
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logging.info("End of partition reached")
                        continue
                    else:
                        logging.error(f"Consumer error: {msg.error()}")
                        raise KafkaException(msg.error())
                logging.info(f"Received message: {msg.value()}")
                callback(json.loads(msg.value()))
        except Exception as e:
            logging.error(f"Error in Kafka consumer: {str(e)}")
        finally:
            self.consumer.close()

kafka_service = KafkaService(brokers='localhost:9092')
