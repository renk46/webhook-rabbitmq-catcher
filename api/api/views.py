"""Views"""
import os
import json
import logging
import pika

from rest_framework.views import APIView
from rest_framework.response import Response

class WebHookGrabber(APIView):
    """Grabber WebHook"""
    def get(self, request, queue=None, scope=None):
        logging.info(request.query_params)
        return Response()

    def post(self, request, queue=None, scope=None):
        logging.info(request.META)
        logging.info(request.body)
        logging.info(request.POST)

        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ.get('RABBIT_HOST', 'localhost'), os.environ.get('RABBIT_PORT', 5672)))
        channel = connection.channel()

        if not queue:
            queue = os.environ.get('RABBIT_QUEUE', 'test_queue')

        if scope:
            queue = f'{queue}-{scope}'

        channel.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)
        channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(request.data, indent=4, default=str), properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))

        channel.close()
        connection.close()

        return Response()
