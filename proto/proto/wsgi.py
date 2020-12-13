#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing as t

import structlog
import uvicorn
from fastapi import APIRouter, Depends, FastAPI
from starlette.requests import Request
from starlette.responses import Response, UJSONResponse

import broker
from entities import Tortoise

logger = structlog.get_logger(__name__)


router = APIRouter()


@router.get("/")
def start(
    request: Request,
    x: t.Optional[str] = "1",
    y: t.Optional[str] = "2",
    publisher: broker.Publisher = Depends(broker.get_publisher),
) -> Response:
    process = Tortoise.build("start", int(x), int(y))
    publisher.publish(broker.TURTLE_BEACH, process)
    logger.info("tortoise sent", channel=broker.TURTLE_BEACH, process=process)
    return UJSONResponse({"status": "ok", "process": process.dump()})


@router.get("/check")
def check(
    request: Request,
    key: t.Optional[str] = "",
    reader: broker.Reader = Depends(broker.get_tortoise_reader),
) -> Response:
    if not key:
        return UJSONResponse({"error": "no key to look for"}, 400)

    message = f"Tortoise {key} last seen at: "
    tortoise = reader.get(key)
    if tortoise:
        message += tortoise.meta.stage
        logger.info(message)
        return UJSONResponse({"status": "ok", "process": tortoise.dump()})
    return UJSONResponse({"status": "suspicious", "message": f"{key} was never seen"})


app = FastAPI(title="Прототип")
app.include_router(router)


@app.on_event("startup")
def startup_event():
    app.state.redis = broker.broker()
    logger.info("redis connected", client=app.state.redis)

    # TODO: move all messaging routing to broker module
    pubsub = app.state.redis.pubsub()
    pubsub.subscribe(**{broker.TURTLE_DEATH: broker.handle_errors})
    thread = pubsub.run_in_thread(sleep_time=0.1)
    debug_msg = "Listen for errors..."
    logger.info(debug_msg, channel=broker.TURTLE_DEATH, thread_name=thread.name)


@app.on_event("shutdown")
def shutdown_event():
    app.state.redis.close()
    logger.info("redis disconnected", client=app.state.redis)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
