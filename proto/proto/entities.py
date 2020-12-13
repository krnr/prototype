#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Entities."""
import json
import typing as t
import uuid

import attr


def _str_uid():
    return str(uuid.uuid4())


@attr.s(auto_attribs=True)
class ProcessMeta:
    """Meta-information about running process"""

    stage: str
    uid: str = attr.ib(factory=_str_uid)
    user: str = attr.ib(factory=_str_uid)


@attr.s(auto_attribs=True)
class ProcessPayload:
    """Actual info to process."""

    x: int
    y: int


@attr.s(auto_attribs=True)
class ProcessError:
    """Error message about a process."""

    error: str


@attr.s(auto_attribs=True)
class Tortoise:
    """A tortoise is a slow, stage-based, distributed process."""

    meta: ProcessMeta
    payload: t.Union[ProcessPayload]

    @classmethod
    def build(cls, stage: str, x: int, y: int):
        meta = ProcessMeta(stage=stage)
        payload = ProcessPayload(x, y)
        return cls(meta, payload)

    @classmethod
    def from_msg(cls, msg: bytes):
        try:
            _json = json.loads(msg.decode())
            meta = ProcessMeta(**_json["meta"])
            if "error" in _json["payload"]:
                payload_cls = ProcessError
            else:
                payload_cls = ProcessPayload
            payload = payload_cls(**_json["payload"])
            return cls(meta, payload)
        except (json.JSONDecodeError, LookupError):
            raise ValueError("Can't handle message")

    def dump(self):
        return attr.asdict(self, recurse=True)
