# base image for carrying dependencies
FROM python:3.8.6-buster AS compile-image

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt /
# base images is used to run tests so we install both sets of deps
RUN pip install -r /requirements.txt

FROM python:3.8.6-slim-buster AS app-image

COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./proto /app

WORKDIR /app
