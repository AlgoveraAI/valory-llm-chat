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

"""This package contains the rounds of LLMChatCompletionAbciApp."""
from abc import ABC
from enum import Enum
from os import sync
from typing import Any, Dict, List, Optional, Set, Tuple, Type, cast

from packages.algovera.skills.chat_completion_abci.payloads import (
    CollectRandomnessPayload,
    ProcessRequestPayload,
    PublishResponsePayload,
    RegistrationPayload,
    SelectKeeperPayload,
    WaitForRequestPayload,
)
from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AbstractRound,
    AppState,
    BaseSynchronizedData,
    CollectSameUntilAllRound,
    CollectSameUntilThresholdRound,
    EventToTimeout,
    OnlyKeeperSendsRound,
    get_name,
)


class Event(Enum):
    """LLMChatCompletionAbciApp Events"""

    ERROR = "error"
    ROUND_TIMEOUT = "round_timeout"
    NO_MAJORITY = "no_majority"
    DONE = "done"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """

    @property
    def printed_messages(self) -> List[str]:
        """Get the printed messages list."""
        return cast(
            List[str],
            self.db.get_strict("printed_messages"),
        )

    @property
    def request_data(self) -> Dict[str, str]:
        """Get the request data."""
        return cast(
            Dict[str, str],
            self.db.get_strict("request_data"),
        )

    @property
    def response_data(self) -> Dict[str, Any]:
        """Get the response data."""
        return cast(
            Dict[str, Any],
            self.db.get_strict("response_data"),
        )


class LLMChatCompletionABCIAbstractRound(AbstractRound, ABC):
    synchronized_data_class: Type[BaseSynchronizedData] = SynchronizedData

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, self._synchronized_data)


class CollectRandomnessRound(
    CollectSameUntilThresholdRound, LLMChatCompletionABCIAbstractRound
):
    """CollectRandomnessRound"""

    payload_class = CollectRandomnessPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.DONE
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.participant_to_randomness)
    selection_key = get_name(SynchronizedData.most_voted_randomness)


class ProcessRequestRound(OnlyKeeperSendsRound, LLMChatCompletionABCIAbstractRound):
    """ProcessRequestRound"""

    payload_class = ProcessRequestPayload

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        if self.keeper_payload:
            payload = self.keeper_payload
            error = payload.response_data["error"]
            if error == "True":
                return self.synchronized_data, Event.ERROR

            synchronized_data = self.synchronized_data.update(
                request_data={},
                response_data=payload.response_data,
                synchronized_data_class=SynchronizedData,
            )

            return synchronized_data, Event.DONE


class PublishResponseRound(OnlyKeeperSendsRound, LLMChatCompletionABCIAbstractRound):
    """PublishResponseRound"""

    payload_class = PublishResponsePayload
    synchronized_data_class = SynchronizedData

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        if self.keeper_payload:
            payload = self.keeper_payload
            published = payload.published
            if published:
                return self.synchronized_data, Event.DONE
            else:
                return self.synchronized_data, Event.ERROR


class RegistrationRound(CollectSameUntilAllRound, LLMChatCompletionABCIAbstractRound):
    """RegistrationRound"""

    payload_class = RegistrationPayload

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""

        if self.collection_threshold_reached:
            synchronized_data = self.synchronized_data.update(
                participants=tuple(sorted(self.collection)),
                synchronized_data_class=SynchronizedData,
            )
            return synchronized_data, Event.DONE
        return None


class SelectKeeperRound(
    CollectSameUntilThresholdRound, LLMChatCompletionABCIAbstractRound
):
    """SelectKeeperRound"""

    payload_class = SelectKeeperPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.DONE
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.participant_to_selection)
    selection_key = get_name(SynchronizedData.most_voted_keeper_address)


class WaitForRequestRound(OnlyKeeperSendsRound, LLMChatCompletionABCIAbstractRound):
    """WaitForRequestRound"""

    payload_class = WaitForRequestPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.DONE

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.keeper_payload:
            payload = self.keeper_payload
            error = payload.request_data["error"]
            if error == "True":
                return self.synchronized_data, Event.ERROR

            synchronized_data = self.synchronized_data.update(
                request_data=payload.request_data,
                synchronized_data_class=SynchronizedData,
            )
            return synchronized_data, Event.DONE


class LLMChatCompletionAbciApp(AbciApp[Event]):
    """LLMChatCompletionAbciApp"""

    initial_round_cls: AppState = RegistrationRound
    initial_states: Set[AppState] = {RegistrationRound}
    transition_function: AbciAppTransitionFunction = {
        RegistrationRound: {Event.DONE: CollectRandomnessRound},
        CollectRandomnessRound: {
            Event.DONE: SelectKeeperRound,
            Event.NO_MAJORITY: CollectRandomnessRound,
            Event.ROUND_TIMEOUT: CollectRandomnessRound,
        },
        ProcessRequestRound: {
            Event.DONE: PublishResponseRound,
            Event.ERROR: RegistrationRound,
        },
        PublishResponseRound: {
            Event.DONE: CollectRandomnessRound,
            Event.ERROR: RegistrationRound,
        },
        SelectKeeperRound: {
            Event.DONE: WaitForRequestRound,
            Event.NO_MAJORITY: RegistrationRound,
            Event.ROUND_TIMEOUT: RegistrationRound,
        },
        WaitForRequestRound: {
            Event.DONE: ProcessRequestRound,
            Event.ERROR: RegistrationRound,
            Event.ROUND_TIMEOUT: WaitForRequestRound,
        },
    }
    final_states: Set[AppState] = set()
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: Set[str] = []
    db_pre_conditions: Dict[AppState, Set[str]] = {
        RegistrationRound: [],
    }
    db_post_conditions: Dict[AppState, Set[str]] = {}
