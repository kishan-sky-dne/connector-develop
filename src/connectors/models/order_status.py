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
# Standard Library
from enum import Enum
from typing import Optional

# Third Party Library
from pydantic import BaseModel, ConfigDict, StrictInt


class StringEnum(str, Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"
    INPROGRESS = "In Progress"
    PARTIALSUCCESS = "Partial Success"
    ABORTED = "Aborted"
    COMPLETE = "Complete"
    FAILED = "Failed"  # Bug Fix - DNE-33816

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        return next((member for member in cls if member.lower() == value), None)


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)
    orderNumber: StrictInt  # noqa: N815
    orderType: str  # noqa: N815
    orderCreatedDate: str  # noqa: N815
    orderEndDate: Optional[str] = None  # noqa: N815
    status: StringEnum
    serviceStatusDetails: Optional[dict] = None  # noqa: N815


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    keyId: str  # noqa: N815
    message: Message
    eventTime: str  # noqa: N815
    eventSource: str  # noqa: N815
