"""Views"""
import os
import json
import logging
import requests

from api.broker import Broker

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class WebHookGrabber(APIView):
    """Grabber WebHook"""
    def get(self, request, app=os.environ.get('RABBIT_DEFAULT_QUEUE', 'main'), scope=None):
        mode = self.request.query_params.get('hub.mode')
        challenge = self.request.query_params.get('hub.challenge')
        token = self.request.query_params.get('hub.verify_token')

        if mode == "subscribe" and token == os.environ.get('FACEBOOK_WEBHOOK_CHECK', '123'):
            return Response(int(challenge))
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def post(self, request, app=os.environ.get('RABBIT_DEFAULT_QUEUE', 'main'), scope=None):
        logging.info(request.META)
        logging.info(request.body)
        logging.info(request.POST)

        body = json.dumps(request.data, indent=4, default=str)
        queue = f'{app}-{scope}' if scope else f'{app}'

        if os.environ.get('PROXY_MODE', False):
            try:
                url = os.environ.get('PROXY_ENDPOINT', 'http://localhost:8888')
                url = f"{url}/{app}" if app else url
                url = f"{url}/{scope}" if scope else url
                headers = {'Content-Type': 'application/json'}
                requests.post(url, body, timeout=30, headers=headers)
            except requests.exceptions.ConnectionError:
                Broker.save_to_broker(body, queue)
        else:
            Broker.save_to_broker(body, queue)

        return Response()

class GrabView(APIView):
    """Grab messages from broker to proxy"""
    def get_and_send_message(self, queue, url, connection = None, count = 0):
        data, channel, connection, method_frame = Broker.get_message(queue, connection)
        if data:
            headers = {'Content-Type': 'application/json'}
            body = json.dumps(data, default=str)
            requests.post(url, body, timeout=30, headers=headers)
            if method_frame.delivery_tag:
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            else:
                channel.basic_reject(delivery_tag=method_frame.delivery_tag)
            return self.get_and_send_message(queue, url, connection, count + 1)
        else:
            channel.close()
            connection.close()
            return count

    def get(self, request, app=os.environ.get('RABBIT_DEFAULT_QUEUE', 'main'), scope=None):
        if not os.environ.get('PROXY_MODE', False): return
        queue = f'{app}-{scope}' if scope else f'{app}'

        url = os.environ.get('PROXY_ENDPOINT', 'http://localhost:8888')
        url = f"{url}/{app}" if app else url
        url = f"{url}/{scope}" if scope else url

        count = self.get_and_send_message(queue, url)

        return Response({
            "result": True,
            "count": count
        })
