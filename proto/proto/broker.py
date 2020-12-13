#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import redis
import structlog

from fastapi import FastAPI
from starlette.requests import Request

from entities import Tortoise

logger = structlog.get_logger(__name__)

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
    if msg["type"] == "message":
        try:
            tortoise = Tortoise.from_msg(msg["data"])
            # inform user?
            logger.error(
                "Tortoise can't move further",
                stage=tortoise.meta.stage,
                error=tortoise.payload,
            )
        except ValueError:
            logger.error("unexpected error", msg=msg)


class Publisher:
    def __init__(self, app: FastAPI):
        self._redis = app.state.redis

    def publish(self, channel: str, process: Tortoise):
        self._redis.set(process.meta.uid, json.dumps(process.dump()).encode())
        self._redis.publish(channel, json.dumps(process.dump()).encode())


class Reader:
    def __init__(self, app: FastAPI, entity_class=Tortoise):
        self._redis = app.state.redis
        self._class = entity_class

    def get(self, key: str):
        msg = self._redis.get(key)
        if msg:
            return self._class.from_msg(msg)


def get_publisher(request: Request):
    return Publisher(app=request.app)


def get_tortoise_reader(request: Request):
    return Reader(app=request.app, entity_class=Tortoise)

