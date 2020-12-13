.. code:: bash

    $ poetry export -f proto/requirements.txt -o proto/requirements.txt --without-hashes
    $ docker build -t ml_proto proto
    $ docker build -t ml_proto_rust some_rust_lib
    $ docker-compose up

.. code::

    ...
    rust_1   | 2020-12-13 08:18.42 Rust lib listens to the start_on_the_beach in Thread-1...
    web_1    | INFO:     Started server process [1]
    web_1    | INFO:     Waiting for application startup.
    web_1    | 2020-12-13 08:18.43 redis connected                client=Redis<ConnectionPool<Connection<host=redis,port=6379,db=0>>>
    web_1    | 2020-12-13 08:18.43 Listen for errors...           channel=/dev/null thread_name=Thread-1
    web_1    | INFO:     Application startup complete.
    web_1    | INFO:     Uvicorn running on http://0.0.0.0:8088 (Press CTRL+C to quit)
    web_1    | 2020-12-13 08:18.55 tortoise sent                  channel=start_on_the_beach process=Tortoise(meta=ProcessMeta(stage='start', uid='439b5777-bb8e-4c49-b485-3ea744ea7efd', user='09b52f08-6cec-4942-b21e-5354c1c881fc'), payload=ProcessPayload(x=1, y=2))
    rust_1   | 2020-12-13 08:18.55 Message in: start_on_the_beach
    rust_1   | 2020-12-13 08:18.55 b'{"meta": {"stage": "start", "uid": "439b5777-bb8e-4c49-b485-3ea744ea7efd", "user": "09b52f08-6cec-4942-b21e-5354c1c881fc"}, "payload": {"x": 1, "y": 2}}'
    web_1    | INFO:     172.22.0.1:46104 - "GET /?x=1&y=2 HTTP/1.1" 200 OK
    rust_1   | 2020-12-13 08:18.55 Sent to: ocean                 msg={'meta': {'stage': 'divider', 'uid': '439b5777-bb8e-4c49-b485-3ea744ea7efd', 'user': '09b52f08-6cec-4942-b21e-5354c1c881fc'}, 'payload': {'result': 0.5}}

    rust_1   | 2020-12-13 08:19.02 Message in: start_on_the_beach
    web_1    | 2020-12-13 08:19.02 tortoise sent                  channel=start_on_the_beach process=Tortoise(meta=ProcessMeta(stage='start', uid='ad5bd01c-798d-4dd0-b13b-6911ecd7fb28', user='106cdd85-4491-419f-bcb2-2ef78a5d497f'), payload=ProcessPayload(x=100, y=0))
    web_1    | INFO:     172.22.0.1:46114 - "GET /?x=100&y=0 HTTP/1.1" 200 OK
    rust_1   | 2020-12-13 08:19.02 b'{"meta": {"stage": "start", "uid": "ad5bd01c-798d-4dd0-b13b-6911ecd7fb28", "user": "106cdd85-4491-419f-bcb2-2ef78a5d497f"}, "payload": {"x": 100, "y": 0}}'
    rust_1   | 2020-12-13 08:19.02 Sent to: /dev/null             msg={'meta': {'stage': 'divider', 'uid': 'ad5bd01c-798d-4dd0-b13b-6911ecd7fb28', 'user': '106cdd85-4491-419f-bcb2-2ef78a5d497f'}, 'payload': {'error': "local variable 'result' referenced before assignment"}}
    web_1    | 2020-12-13 08:19.02 Tortoise can't move further    error=ProcessError(error="local variable 'result' referenced before assignment") stage=divider

