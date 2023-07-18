# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2023 Valory AG
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

"""This module contains the handlers for the skill of LLMChatCompletionAbciApp."""

from typing import Optional

from aea.configurations.data_types import PublicId

from packages.algovera.protocols.chat_completion.message import ChatCompletionMessage
from packages.algovera.protocols.rabbitmq.message import RabbitmqMessage
from packages.valory.skills.abstract_round_abci.handlers import (
    ABCIRoundHandler as BaseABCIRoundHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import AbstractResponseHandler
from packages.valory.skills.abstract_round_abci.handlers import (
    ContractApiHandler as BaseContractApiHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    HttpHandler as BaseHttpHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    IpfsHandler as BaseIpfsHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    LedgerApiHandler as BaseLedgerApiHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    SigningHandler as BaseSigningHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    TendermintHandler as BaseTendermintHandler,
)


class ChatCompletionHandler(AbstractResponseHandler):
    SUPPORTED_PROTOCOL: Optional[PublicId] = ChatCompletionMessage.protocol_id
    allowed_response_performatives = frozenset(
        {
            ChatCompletionMessage.Performative.REQUEST,
            ChatCompletionMessage.Performative.RESPONSE,
        }
    )


class RabbitmqHandler(AbstractResponseHandler):
    SUPPORTED_PROTOCOL: Optional[PublicId] = RabbitmqMessage.protocol_id
    allowed_response_performatives = frozenset(
        {
            RabbitmqMessage.Performative.CONSUME_REQUEST,
            RabbitmqMessage.Performative.PUBLISH_REQUEST,
            RabbitmqMessage.Performative.CONSUME_RESPONSE,
            RabbitmqMessage.Performative.PUBLISH_RESPONSE,
        }
    )


ABCIHandler = BaseABCIRoundHandler
HttpHandler = BaseHttpHandler
SigningHandler = BaseSigningHandler
LedgerApiHandler = BaseLedgerApiHandler
ContractApiHandler = BaseContractApiHandler
TendermintHandler = BaseTendermintHandler
IpfsHandler = BaseIpfsHandler
