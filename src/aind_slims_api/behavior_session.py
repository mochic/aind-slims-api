"""Contains a model for the mouse content, and a method for fetching it"""

import logging
from typing import Any
from datetime import date as _date

from pydantic import Field, ValidationError

from aind_slims_api.core import SlimsBaseModel, SlimsClient, SLIMSTABLES

logger = logging.getLogger()


class SlimsBehaviorSessionContentEvent(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent"""

    mouse_name: str | None = Field(default=None, alias="cnvn_fk_content")  # used as reference to mouse
    notes: str = Field(..., alias="cnvn_cf_notes")
    task_stage: str = Field(..., alias="cnvn_cf_taskStage")
    instrument: str = Field(..., alias="cnvn_cf_fk_instrument")  # TODO: Check if we want to use str for this, Dynamic Choice
    trainer: str = Field(..., alias="cnvn_cf_fk_trainer")  # TODO: Check if we want to use str for this, Dynamic Choice
    task: str = Field(..., alias="cnvn_cf_task")
    is_curriculum_suggestion: bool = Field(
        ..., alias="cnvn_cf_stageIsOnCurriculum")
    task_version: str = Field(..., alias="cnvn_cf_taskSchemaVersion")
    software_version: str | None = Field(
        default=None, alias="cnvn_cf_softwareVersion")
    date: _date = Field(..., alias="cnvn_cf_scheduledDate")

    _slims_table: SLIMSTABLES = "ContentEvent"


def fetch_behavior_session_content_events(
    client: SlimsClient,
    mouse_name: str,
) -> list[SlimsBehaviorSessionContentEvent | dict[str, Any]]:
    """Fetches behavior sessions for a mouse with labtracks id {mouse_name}"""
    response = client.fetch(
        SlimsBehaviorSessionContentEvent._slims_table,
        cnvn_fk_content=mouse_name,
        sort="cnvn_cf_scheduledDate",
    )

    validated: list[SlimsBehaviorSessionContentEvent | dict[str, Any]] = []
    for behavior_session in response:
        try:
            validated.append(
                SlimsBehaviorSessionContentEvent
                .model_validate(behavior_session)
            )
        except ValidationError as e:
            logger.error(f"SLIMS data validation failed, {repr(e)}")
            validated.append(behavior_session.json_entity)

    return validated


def write_behavior_session_content_events(
    client: SlimsClient,
    mouse_name: str,
    *behavior_sessions: SlimsBehaviorSessionContentEvent,
) -> list[SlimsBehaviorSessionContentEvent]:
    """Writes behavior sessions for a mouse with labtracks id {mouse_name}

    Notes
    -----
    - All supplied `behavior_sessions` will have their `mouse_name` field set
     to the value supplied as `mouse_name` to this function
    """
    added = []
    for behavior_session in behavior_sessions:
        updated = behavior_session.model_copy(
            update={"mouse_name": mouse_name})
        try:
            validated = SlimsBehaviorSessionContentEvent.model_validate(updated)
        except ValidationError as e:
            logger.error(
                f"SLIMS data validation failed. Skipping write, {repr(e)}")
            continue
        added.append(client.add_model(validated))

    return added
