#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import typing as t

import redis
import structlog
import uvicorn
from fastapi import APIRouter, Depends, FastAPI
from starlette.requests import Request
from starlette.responses import Response, UJSONResponse

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


router = APIRouter()


@router.get("/")
def start(request: Request, x: t.Optional[str] = "1", y: t.Optional[str] = "2", publisher: Publisher = Depends(_get_publisher)) -> Response:
    process = Tortoise.build("start", int(x), int(y))
    publisher.publish(TURTLE_BEACH, process)
    logger.info(f"tortoise sent to {TURTLE_BEACH}", process=process)
    return UJSONResponse({"status": "ok", "process": process.dump()})


app = FastAPI(title="Прототип")
app.include_router(router)


@app.on_event("startup")
def startup_event():
    app.state.redis = broker()
    logger.info("redis connected", client=app.state.redis)

    pubsub = app.state.redis.pubsub()
    pubsub.subscribe(**{TURTLE_DEATH: handle_errors})
    thread = pubsub.run_in_thread(sleep_time=0.1)
    debug_msg = 'Listen for errors...'
    logger.info(debug_msg, channel=TURTLE_DEATH, thread_name=thread.name)

@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()
    logger.info("redis disconnected", client=app.state.redis)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8088)

