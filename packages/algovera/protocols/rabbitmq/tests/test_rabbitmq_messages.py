# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2023 algovera
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Test messages module for rabbitmq protocol."""

# pylint: disable=too-many-statements,too-many-locals,no-member,too-few-public-methods,redefined-builtin
from typing import List

from aea.test_tools.test_protocol import BaseProtocolMessagesTestCase

from packages.algovera.protocols.rabbitmq.message import RabbitmqMessage


class TestMessageRabbitmq(BaseProtocolMessagesTestCase):
    """Test for the 'rabbitmq' protocol message."""

    MESSAGE_CLASS = RabbitmqMessage

    def build_messages(self) -> List[RabbitmqMessage]:  # type: ignore[override]
        """Build the messages to be used for testing."""
        return [
            RabbitmqMessage(
                performative=RabbitmqMessage.Performative.CONSUME_REQUEST,
                rabbitmq_details={"some str": "some str"},
                consume_queue_name="some str",
            ),
            RabbitmqMessage(
                performative=RabbitmqMessage.Performative.CONSUME_RESPONSE,
                consume_response={"some str": "some str"},
            ),
            RabbitmqMessage(
                performative=RabbitmqMessage.Performative.PUBLISH_REQUEST,
                rabbitmq_details={"some str": "some str"},
                publish_queue_name="some str",
                publish_message={"some str": "some str"},
            ),
            RabbitmqMessage(
                performative=RabbitmqMessage.Performative.PUBLISH_RESPONSE,
                publish_response={"some str": "some str"},
            ),
        ]

    def build_inconsistent(self) -> List[RabbitmqMessage]:  # type: ignore[override]
        """Build inconsistent messages to be used for testing."""
        return [
            RabbitmqMessage(
                performative=RabbitmqMessage.Performative.CONSUME_REQUEST,
                # skip content: rabbitmq_details
                consume_queue_name="some str",
            ),
            RabbitmqMessage(
                performative=RabbitmqMessage.Performative.CONSUME_RESPONSE,
                # skip content: consume_response
            ),
            RabbitmqMessage(
                performative=RabbitmqMessage.Performative.PUBLISH_REQUEST,
                # skip content: rabbitmq_details
                publish_queue_name="some str",
                publish_message={"some str": "some str"},
            ),
            RabbitmqMessage(
                performative=RabbitmqMessage.Performative.PUBLISH_RESPONSE,
                # skip content: publish_response
            ),
        ]
