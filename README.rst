This is an example of pipeline errors handling while complying to "12factor" principles:

- we have several stateless processes (`proto` and `some_rust_lib`)
- `proto` handles web requests and may inform user about errors in the pipeline
- each spawned message has unique ID and user information (about who spawned it)
- messages are routed via any broker (Redis Pub/Sub, RabbitMQ, you-name-it)
- it's the process' responsibility to send a signal to a broker when the process can't handle message 
- when the process is killed or dies silently - it's infrastructure problem and can be monitored (but not managed!) via "search-for-lost-turtles" mechanism
- every stage records turtles seen and we may set ttl for such updates to consider every record past some threshold as "lost"

.. code:: bash

    $ cd proto && poetry export -f requirements.txt -o requirements.txt --without-hashes && cd -
    $ docker build -t ml_proto proto
    $ docker build -t ml_proto_rust some_rust_lib
    $ docker-compose up
    $ MUST_RETURN=$(http http://127.0.0.1:8088/\?x\=1\&y\=2 | jq '.process.meta.uid')
    $ GOT_LOST=$(http http://127.0.0.1:8088/\?x\=100000\&y\=2 | jq '.process.meta.uid')


.. code::

    ...
    rust_1   | 2020-12-13 08:18.42 Rust lib listens to the start_on_the_beach in Thread-1...
    web_1    | INFO:     Started server process [1]
    web_1    | INFO:     Waiting for application startup.
    web_1    | 2020-12-13 08:18.43 redis connected                client=Redis<ConnectionPool<Connection<host=redis,port=6379,db=0>>>
    web_1    | 2020-12-13 08:18.43 Listen for errors...           channel=/dev/null thread_name=Thread-1
    web_1    | INFO:     Application startup complete.
    web_1    | INFO:     Uvicorn running on http://0.0.0.0:8088 (Press CTRL+C to quit)

    rust_1   | 2020-12-13 09:19.51 Message in: start_on_the_beach
    rust_1   | 2020-12-13 09:19.51 b'{"meta": {"stage": "start", "uid": "c6956e79-3f38-4b32-a971-c8d746cb518e", "user": "4389061a-0db9-49bc-9ed3-b9f64259d04e"}, "payload": {"x": 1, "y": 2}}'
    web_1    | 2020-12-13 09:19.51 tortoise sent                  channel=start_on_the_beach process=Tortoise(meta=ProcessMeta(stage='start', uid='c6956e79-3f38-4b32-a971-c8d746cb518e', user='4389061a-0db9-49bc-9ed3-b9f64259d04e'), payload=ProcessPayload(x=1, y=2))
    web_1    | INFO:     172.22.0.1:55092 - "GET /?x=1&y=2 HTTP/1.1" 200 OK
    rust_1   | 2020-12-13 09:19.51 Message last seen at DIVIDE    uid=c6956e79-3f38-4b32-a971-c8d746cb518e
    rust_1   | 2020-12-13 09:19.51 Sent to: ocean                 msg={'meta': {'stage': 'divider', 'uid': 'c6956e79-3f38-4b32-a971-c8d746cb518e', 'user': '4389061a-0db9-49bc-9ed3-b9f64259d04e'}, 'payload': {'result': 0.5}}
    web_1    | 2020-12-13 09:19.56 tortoise sent                  channel=start_on_the_beach process=Tortoise(meta=ProcessMeta(stage='start', uid='b5048bdb-72f8-4015-a6af-a80d9067eb79', user='aeb56322-071a-4145-acee-9edaab1993d0'), payload=ProcessPayload(x=100000, y=2))
    web_1    | INFO:     172.22.0.1:55100 - "GET /?x=100000&y=2 HTTP/1.1" 200 OK
    rust_1   | 2020-12-13 09:19.56 Message in: start_on_the_beach
    rust_1   | 2020-12-13 09:19.56 b'{"meta": {"stage": "start", "uid": "b5048bdb-72f8-4015-a6af-a80d9067eb79", "user": "aeb56322-071a-4145-acee-9edaab1993d0"}, "payload": {"x": 100000, "y": 2}}'


.. code:: bash

    $ http http://127.0.0.1:8088/check\?key\=${MUST_RETURN:1:-1}
    $ http http://127.0.0.1:8088/check\?key\=${GOT_LOST:1:-1}

.. code::

    web_1    | 2020-12-13 09:20.00 Tortoise c6956e79-3f38-4b32-a971-c8d746cb518e last seen at: divider
    web_1    | INFO:     172.22.0.1:55104 - "GET /check?key=c6956e79-3f38-4b32-a971-c8d746cb518e HTTP/1.1" 200 OK
    web_1    | 2020-12-13 09:20.04 Tortoise b5048bdb-72f8-4015-a6af-a80d9067eb79 last seen at: start
    web_1    | INFO:     172.22.0.1:55108 - "GET /check?key=b5048bdb-72f8-4015-a6af-a80d9067eb79 HTTP/1.1" 200 OK

