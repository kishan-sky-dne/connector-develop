"""
__author__ = "Sky UK Ltd"
__copyright__ = Copyright © Sky CP Limited 2023.
All rights reserved. No part of this work may be reproduced,
stored in a retrieval system of any nature, or transmitted,
in any form or by any means including photocopying
and recording, without the prior written permission of Sky,
the copyright owner.
__licence__ = "subject to the terms of the licence with Sky UK Ltd'
__version__ = "1.0"
"""
# Third Party Library
from setuptools import find_packages, setup

setup(
    name="connectors",
    version="0.1.0",
    description="Service responsible for enabling the link between modules",
    author="IPND",
    author_email="DL-netauto-dev@sky.uk",
    keywords="connectors",
    license="SKY",
    url="https://scm.isp.sky.com/network-automation/components/connectors",
    python_requires="~=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    zip_safe=False,
    install_requires=[
        "connexion==2.14.1",
        "pyjwt==2.5.0",
        "python_dateutil==2.8.0",
        "flask==2.2.5",
        "xlrd==1.2.0",
        "xlwt==1.3.0",
        "xlutils==2.0.0",
        "python-json-logger==0.1.11",
        "pymongo==3.12.0",
        (
            "dne-config @ "
            "https://github.com/sky-uk/dne-config/releases/download/release/1.0.0/dne_config-1.0.0-py3-none-any.whl"
        ),
        "requests==2.31.0",
        "jinja2==3.1.3",
        "jsonschema==4.4.0",
        "openapi-spec-validator==0.4.0",
        "sqlalchemy==1.3.20",
        "PyMySQL==1.1.1",
        "Werkzeug==2.3.8",
        "msal==1.27.0",
        "pytz==2023.3",
        "aiohttp==3.9.4",
        "backoff==2.2.1",
        "confluent-kafka==2.3.0",
        "elasticsearch==7.17.9",
        "pydantic==2.4.2",
        "nested_lookup==0.2.25",
        "minio==7.2.11",
        "zstd==1.5.5.1",
        "pytest-asyncio==0.24.0",
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: SKY License",
        "Intended Audience :: Developers",
        "Intended Audience :: SysAdmins",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
