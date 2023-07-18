import os
import pika
import json

class Broker:
    """Class Broker"""

    @staticmethod
    def get_connection():
        """Get connection"""
        credentials = pika.PlainCredentials(os.environ.get('RABBIT_USER', "guest"), os.environ.get('RABBIT_PASS', "guest"))
        parameters = pika.ConnectionParameters(
            host=os.environ.get('RABBIT_HOST', "localhost"),
            port=os.environ.get('RABBIT_PORT', 5672),
            heartbeat=os.environ.get('RABBIT_HEARTBEAT', 6000),
            blocked_connection_timeout=os.environ.get('RABBIT_BLOCKED_CONNECTION_TIMEOUT', 300),
            credentials=credentials
        )
        return pika.BlockingConnection(parameters)

    @staticmethod
    def save_to_broker(body, queue):
        """Save to broker"""
        connection = Broker.get_connection()
        channel = connection.channel()

        channel.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)
        channel.basic_publish(exchange='', routing_key=queue, body=body, properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))

        channel.close()
        connection.close()

    @staticmethod
    def get_message(queue, connection = None):
        """Get message from broker"""
        connection = connection or Broker.get_connection()
        channel = connection.channel()
        queue_obj = channel.queue_declare(queue=queue, durable=True)
        if queue_obj.method.message_count > 0:
            method_frame, header_frame, msg = channel.basic_get(queue=queue, auto_ack=False) # pylint: disable=W0612
            if method_frame and (method_frame.NAME in ['Basic.GetOk', 'Basic.Deliver']):
                try:
                    data_str_json = msg.decode() if msg else False
                    data = json.loads(data_str_json)
                    return data, channel, connection, method_frame
                except Exception as exception: # pylint: disable=W0718
                    print(exception)
        return False, channel, connection, False
