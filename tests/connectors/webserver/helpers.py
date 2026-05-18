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
# DNE Library
from connectors.core.exceptions import ServiceDBException
from connectors.core.services.itsm.exceptions import DateGeneratorError, DateValidateError, InvalidRequest
from connectors.core.utils.exceptions import (
    ConflictException,
    ConnectorException,
    ResourceServiceNotAvailable,
    RestUtilityException,
    UnauthorizedException,
)

exception_cmd_apis = [
    (UnauthorizedException, 401),
    (ResourceServiceNotAvailable, 404),
    (RestUtilityException, 403),
    (ConnectorException, 500),
    (ValueError, 400),
    (InvalidRequest, 400),
    (DateGeneratorError, 400),
    (DateValidateError, 400),
    (ConflictException, 409),
    (ServiceDBException, 403),
    (KeyError, 400),
    (AttributeError, 400),
    (Exception, 500),
]
