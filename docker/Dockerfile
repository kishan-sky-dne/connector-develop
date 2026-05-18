# """
# __author__ = "Sky UK Ltd"
# __copyright__ = Copyright © Sky CP Limited 2023.
# All rights reserved. No part of this work may be reproduced,
# stored in a retrieval system of any nature, or transmitted,
# in any form or by any means including photocopying
# and recording, without the prior written permission of Sky,
# the copyright owner.
# __licence__ = "subject to the terms of the licence with Sky UK Ltd'
# __version__ = "1.0"
# """
FROM registry.cloud.sky/ipnd-dne-public/python:3.10-sky as BASE

COPY requirements.txt requirements.txt
RUN apt update && apt install -y gcc musl-dev snmpd snmp libsnmp-dev python3-dev libffi-dev libssl-dev make ca-certificates dos2unix
RUN pip wheel --wheel-dir=/tmp/wheels -r requirements.txt

FROM registry.cloud.sky/ipnd-dne-public/python:3.10-sky as RELEASE

LABEL version="0.1.0"

# Setting the requests library certificate store for sky's internal CA
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

# Setting environment variables , needs to be updated/removed
ENV UWSGI_INI /app/config/uwsgi.ini

# Setup FS
WORKDIR /
RUN mkdir /app
RUN mkdir -p /app/config
RUN mkdir -p /app/openapi
RUN mkdir -p /app/templates


# copying third-party wheels
COPY --from=BASE /tmp/wheels /tmp/wheels
COPY requirements.txt /app/requirements.txt
COPY dist/ /app/dist/
COPY templates/ /app/templates
COPY openapi/openapi.yaml /app/openapi/openapi.yaml
COPY json_schema/ /app/json_schema/
COPY docker/connectors/jwt-key-common.pub /app
COPY docker/connectors/jwt-key-master.pub /app
COPY docker/connectors/config/connectors.conf /app/config/connectors.conf
COPY docker/connectors/config/uwsgi.ini /app/config/uwsgi.ini
COPY scripts/entrypoint.sh /app/entrypoint.sh
COPY docker/connectors/sky_internal_cas.crt /usr/local/share/ca-certificates/sky_internal_cas.crt

# Removing the Control M characters created during DOCKER COPY
RUN dos2unix /usr/local/share/ca-certificates/*

RUN update-ca-certificates

RUN apt update && apt install tzdata
# Setting environment variables for Node to have BST/GMT
ENV TZ=Europe/London
RUN mkdir -p /usr/share/zoneinfo/ &&  cp /usr/share/zoneinfo/Europe/London /etc/localtime

RUN mkdir -p /var/log/connectors/ && \
# installing third-party wheels copied from the BASE release
    pip install -r /app/requirements.txt --find-links=/tmp/wheels/ && \
# installing python libraries from isp scm
    pip install /app/dist/isp-config* && \
# installing connector
    pip install --no-deps /app/dist/connectors* && \
    rm -r /app/dist/* /tmp/wheels


ENTRYPOINT ["sh", "/app/entrypoint.sh"]
