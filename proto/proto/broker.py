#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import redis

from fastapi import FastAPI
from starlette.requests import Request
from entities import Tortoise

# config

## Redis channels

TURTLE_BEACH = "start_on_the_beach"  # where the life begins...
TURTLE_DEATH = "/dev/null"  # ...and stops


# TODO: @retry(errors=[redis.ConnectionError], ...)
def broker():
    r = redis.StrictRedis(host="redis")
    r.client_list()  # used to check the connection
    return r


def handle_errors(msg: bytes):
    if msg['type'] == 'message':
        try:
            tortoise = Tortoise.from_msg(msg['data'])
            # inform user?
            logger.error("Tortoise can't move further", stage=tortoise.meta.stage, error=tortoise.payload)
        except ValueError:
            logger.error("unexpected error", msg=msg)


class Publisher:
    def __init__(self, app: FastAPI):
        self._redis = app.state.redis

    def publish(self, channel: str, process: Tortoise):
        self._redis.publish(channel, json.dumps(process.dump()).encode())


def _get_publisher(request: Request):
    return Publisher(app=request.app)


