#!/usr/bin/env python
# encoding: utf-8

import os
import hashlib
import json
import logging
import signal
import time
import uuid
from redis import Redis

from urlparse import urlparse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.crypto import constant_time_compare

from tornado.ioloop import IOLoop
from tornado.web import HTTPError
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from tornado.options import define, parse_command_line, options
from tornadoredis import Client
from tornadoredis.pubsub import BaseSubscriber


define('debug', default=False, type=bool, help='run in debug mode')
define('port', default=8080, type=int, help='server port')
define('allowed_hosts', default='localhost:8080', multiple=True,
       help='allowed hosts for cross domain connections')


class RedisSubScriber(BaseSubscriber):

    def on_message(self, msg):
        """ handle new message on the redis channle. """
        if msg and msg.kind == 'message':
            try:
                message = json.loads(msg.body)
                sender = message['sender']
                message = message['message']
            except (ValueError, KeyError):
                message = msg.body
                sender = None

            subscribers = list(self.subscribers[msg.channel].keys())
            for subscriber in subscribers:
                try:
                    subscriber.write_message(msg.body)
                except WebSocketClosedError:
                    # remove dead peer
                    self.unsubscribe(msg.channel, subscriber)
        super(RedisSubScriber, self).on_message(msg)


class SprintHandler(WebSocketHandler):
    """ handles real-time updates to the board """

    def check_origin(self, origin):
        allowed = super(SprintHandler, self).check_origin(origin)
        parsed = urlparse(origin.lower())
        matched = any(parsed.netloc == host for host in options.allowed_hosts)
        return options.debug or allowed or matched

    def open(self, sprint):
        """ subscribe to sprint updates on a new connection """
        self.sprint = sprint.decode('utf-8')
        channel = self.get_argument('channel', None)
        if not channel:
            self.close()
        else:
            try:
                self.sprint = self.application.signer.unsign(channel,
                                                             max_age=60 * 30)
            except (BadSignature, SignatureExpired):
                self.close()
            else:
                self.uid = uuid.uuid4().hex
                self.application.add_subscriber(self.sprint, slef)

    def on_message(self, message):
        """ broadcast updates to other interested clients """
        if self.sprint is not None:
            self.application.broadcast(message, channel=self.sprint, sender=self)

    def on_close(self):
        """ remove subscription """
        if self.sprint is not None:
            self.application.remove_subscriber(self.sprint, self)


class UpdateHandler(RequestHandler):
    """ handle updates from django application """

    def post(self, model, pk):
        self._broadcast(model, pk, 'add')

    def put(self, model, pk):
        self._broadcast(model, pk, 'update')

    def delete(self, model, pk):
        self._broadcast(model, pk, 'remove')

    def _broadcast(self, model, pk, action):
        signature = self.request.headers.get('X-Signature', None)
        if not signature:
            raise HTTPEorr(400)
        try:
            result = self.application.signer.unsign(signature, max_age=60 * 1)
        except (BadSignature, SignatureExpired):
            raise HTTPError(400)
        else:
            expected = '{method}:{url}:{body}'.format(
                method=self.request.method.lower(),
                url=self.request.full_url(),
                body=hashlib.sha256(self.request.body).hexdigest()
            )
            if not constant_time_compare(result, expected):
                raise HTTPError(400)
        try:
            body = json.loads(self.request.body.decode('utf-8'))
        except ValueError:
            body = None

        message = json.dumps({
            'model': model,
            'id': pk,
            'action': action,
            'body': body,
        })
        self.application.broadcast(message)
        self.write('Ok')


class ScrumApplication(Application):

    def __init__(self, **kw):
        routes = [
            (r'/socket', SprintHandler),
            (r'/(?P<model>task|sprint|user)/(?P<pk>[0-9]+)', UpdateHandler),
        ]
        super(ScrumApplication, self).__init__(routes, **kw)
        self.subscriber = RedisSubScriber(Client())
        self.publisher = Redis()
        self._key = os.environ.get('WATERCOOLER_SECRET', 'ptyz1dzMeVU')
        self.singer = TimestampSigner(self._key)

    def add_subscriber(self, channel, subscriber):
        self.subscriber.subscribe(['all', channel], subscriber)

    def remove_subscriber(self, channel, subscriber):
        self.subscriber.unsubscribe(channel, subscriber)
        self.subscriber.unsubscribe('all', subscriber)

    def broadcast(self, message, channel=None, sender=None):
        channel = 'all' if channel is None else channel
        message = json.dumps({
            'sender': sender and sender.uid,
            'message': message
        })
        self.publisher.publish(channel, message)


def shutdown(server):
    ioloop = IOLoop.instance()
    logging.info("stopping server.")
    server.stop()

    def finalize():
        ioloop.stop()
        logging.info('stopped')

    ioloop.add_timeout(time.time() + 1.5, finalize)

if __name__ == "__main__":
    parse_command_line()

    application = ScrumApplication(debug=options.debug)
    server = HTTPServer(application)
    server.listen(options.port)

    signal.signal(signal.SIGINT, lambda sig, frame: shutdown(server))
    logging.info("start server on localhost:{}".format(options.port))

    IOLoop.instance().start()
