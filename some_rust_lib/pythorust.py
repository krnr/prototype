#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Suddenly part of the pipeline is written in another language.

We'll try to imitate."""
import json

import redis
import structlog

logger = structlog.get_logger(__name__)


CHANNEL = "start_on_the_beach"
CHANNEL_OUT = "ocean"
CHANNEL_ERROR = "/dev/null"


def process_msg(msg):
    if msg['type'] == 'message':
        logger.info("Message in: " + msg.get('channel').decode())
        logger.info(msg['data'])
        tortoise = json.loads(msg['data'].decode())
        meta = tortoise["meta"]
        meta["stage"] = "divider"
        try:
            divider(tortoise)
        except Exception as ex:
            msg = {"meta": tortoise["meta"], "payload": {"error": str(ex)}}
            error(msg)


def divider(tortoise):
    x = tortoise["payload"]["x"]
    y = tortoise["payload"]["y"]
    try:
        result = x / y
    except ZeroDivisionError:
        pass
    msg = {"meta": tortoise["meta"], "payload": {"result": result}}
    publish(msg)


def publish(msg):
    redis.StrictRedis(host="redis").publish(CHANNEL_OUT, json.dumps(msg).encode())
    logger.info(f"Sent to: {CHANNEL_OUT}", msg=msg)


def error(msg):
    redis.StrictRedis(host="redis").publish(CHANNEL_ERROR, json.dumps(msg).encode())
    logger.info(f"Sent to: {CHANNEL_ERROR}", msg=msg)


if __name__ == "__main__":
    pubsub = redis.StrictRedis(host="redis").pubsub()
    pubsub.subscribe(**{CHANNEL: process_msg})
    thread = pubsub.run_in_thread(sleep_time=0.1)
    debug_msg = 'Rust lib listens to the {} in {}...'
    logger.info(debug_msg.format(CHANNEL, thread.name))

