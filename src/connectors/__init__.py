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
# __version__ = "0.1.0"

# Standard Library
import logging
import os
import sys

# Third Party Library
import connexion
from flask import jsonify

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.utils import log


def create_app(**kwargs):
    connexion_logger = logging.getLogger("connexion")
    connexion_logger.setLevel(logging.DEBUG)

    config_logger = logging.getLogger("isp_config")
    log.setup_logger(config_logger)

    logger = logging.getLogger(__name__)
    log.setup_logger(logger)
    logger.info("App is starting")

    try:
        config = connectors_config.ConnectorsConfigManager()
        config.load_config()
    except ConfigManagerException:
        sys.exit(1)

    conf_logger = config.get(section="options", key="log_level")
    conf_logger = connectors_config.ConnectorsConfigManager.convert_log_setting(conf_logger)
    logger.setLevel(conf_logger)

    spec_file = config.get(section="internals", key="spec_file")
    path = os.path.dirname(spec_file)
    filename = os.path.basename(spec_file)
    options = {"swagger_ui": True, "swagger_json": True}

    connexion_app = connexion.App(__name__, specification_dir=path, options=options)
    connexion_app.add_api(filename, strict_validation=True)

    # Error handlers
    def bad_request(error):
        return jsonify(message=error.description), 400

    def unauthorized(error):
        return jsonify(message=error.description), 401

    def forbidden(error):
        return jsonify(message=error.description), 403

    def not_found(error):
        return jsonify(message=error.description), 404

    def internal_error(error):
        logger.error(error)
        return jsonify(message="Internal Error"), 500

    def error_response(error):
        return jsonify(message=error.description), error.code

    # Register error handlers
    app = connexion_app
    app.app.register_error_handler(400, bad_request)
    app.app.register_error_handler(401, unauthorized)
    app.app.register_error_handler(403, forbidden)
    app.app.register_error_handler(404, not_found)
    app.app.register_error_handler(500, internal_error)

    return app.app
