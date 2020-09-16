import kafka
from logging import getLogger

logger = getLogger(__name__)

def kafkaConnect(BROKER):

	producer = kafka.KafkaProducer(bootstrap_servers=BROKER,max_request_size=15728640)
	logger.info("[kafkaConnect] kafka broker ({}) is connected".format(str(BROKER)))

	return producer


def kafkaPubContent(producer, MESSAGE, TOPIC):

	MESSAGE = MESSAGE.encode('utf-8')

	producer.send(TOPIC, MESSAGE)
	logger.info("[kafkaPub] publish complete!")


def kafkaSubContent(BROKER, TOPIC):

	consumer = kafka.KafkaConsumer(bootstrap_servers=BROKER,fetch_max_bytes=15728640)
	consumer.subscribe([TOPIC])
	return consumer
