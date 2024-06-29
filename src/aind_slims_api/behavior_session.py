"""Contains a model for the mouse content, and a method for fetching it"""

import logging
from typing import Any
from datetime import datetime

from pydantic import Field, ValidationError

from aind_slims_api.core import SlimsBaseModel, SlimsClient, SLIMSTABLES
from aind_slims_api.mouse import fetch_mouse_content, SlimsMouseContent
from aind_slims_api.user import fetch_user, SlimsUser
from aind_slims_api.instrument import fetch_instrument_content, SlimsInstrument

logger = logging.getLogger()


class SlimsBehaviorSessionContentEvent(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent"""

    pk: int | None = Field(default=None, alias="cnvn_pk")
    mouse_name: int | None = Field(
        default=None, alias="cnvn_fk_content")  # used as reference to mouse
    notes: str | None = Field(default=None, alias="cnvn_cf_notes")
    task_stage: str | None = Field(default=None, alias="cnvn_cf_taskStage")
    instrument: int | None = Field(
        default=None, alias="cnvn_cf_fk_instrument")
    trainers: list[int] = Field(
        default=[], alias="cnvn_cf_fk_trainer")
    task: str | None = Field(default=None, alias="cnvn_cf_task")
    is_curriculum_suggestion: bool | None = Field(
        default=None, alias="cnvn_cf_stageIsOnCurriculum")
    task_schema_version: str | None = Field(
        default=None, alias="cnvn_cf_taskSchemaVersion")
    software_version: str | None = Field(
        default=None, alias="cnvn_cf_softwareVersion")
    date: datetime | None = Field(..., alias="cnvn_cf_scheduledDate")

    cnvn_fk_contentEventType: int = 10  # pk of Behavior Session ContentEvent

    _slims_table: SLIMSTABLES = "ContentEvent"


def _fetch_mouse_pk(
    client: SlimsClient,
    mouse_name: str,
) -> int | None:
    """Utility function shared across read/write

    Notes
    -----
    - TODO: Change return type of fetch_mouse_content to match pattern in
     fetch_behavior_session_content_events, or the other way around?
    """
    mouse = fetch_mouse_content(client, mouse_name)
    if isinstance(mouse, dict):
        return mouse["pk"]
    elif isinstance(mouse, SlimsMouseContent):
        return mouse.pk
    elif mouse is None:
        logger.warning(f"No mouse found with name {mouse_name}")
        return None
    else:
        raise ValueError(
            "Unexpected return type from fetch_mouse_content: %s"
            % type(mouse)
        )


def fetch_behavior_session_content_events(
    client: SlimsClient,
    mouse_name: str,
) -> tuple[list[SlimsBehaviorSessionContentEvent], list[dict[str, Any]]]:
    """Fetches behavior sessions for a mouse with labtracks id {mouse_name}

    Returns
    -------
    tuple:
        list:
            Validated SlimsBehaviorSessionContentEvent objects
        list:
            Dictionaries representations of objects that failed validation
    """
    mouse_pk = _fetch_mouse_pk(client, mouse_name)
    logger.debug(f"Mouse pk: {mouse_pk}")
    if mouse_pk is None:
        return [], []

    return client.fetch_models(
        SlimsBehaviorSessionContentEvent,
        cnvn_fk_content=mouse_pk,
        cnvt_name="Behavior Session",
        sort=["cnvn_cf_scheduledDate"],
    )


def write_behavior_session_content_events(
    client: SlimsClient,
    mouse_name: str,
    instrument_name: str,
    trainer_names: list[str],
    *behavior_sessions: SlimsBehaviorSessionContentEvent,
) -> list[SlimsBehaviorSessionContentEvent]:
    """Writes behavior sessions for a mouse with labtracks id {mouse_name}

    Notes
    -----
    - All supplied `behavior_sessions` will have their `mouse_name` field set
     to the value supplied as `mouse_name` to this function
    """
    mouse_pk = _fetch_mouse_pk(client, mouse_name)
    logger.debug(f"Mouse pk: {mouse_pk}")
    if mouse_pk is None:
        raise ValueError(f"No mouse found with name {mouse_name}")
    instrument = fetch_instrument_content(client, instrument_name)
    if isinstance(instrument, dict):
        instrument_pk = instrument["pk"]
    elif isinstance(instrument, SlimsInstrument):
        instrument_pk = instrument.pk
    elif instrument is None:
        raise ValueError(f"No instrument found with name {instrument_name}")
    else:
        raise ValueError(
            "Unexpected return type from fetch_instrument_content: %s"
            % type(instrument)
        )
    trainer_pks = []
    for trainer_name in trainer_names:
        trainer = fetch_user(client, trainer_name)
        if isinstance(trainer, dict):
            trainer_pks.append(trainer["pk"])
        elif isinstance(trainer, SlimsUser):
            trainer_pks.append(trainer.pk)
        elif trainer is None:
            raise ValueError(f"No trainer found with name {trainer_name}")
        else:
            raise ValueError(
                "Unexpected return type from fetch_user: %s"
                % type(trainer)
            )
    added = []
    for behavior_session in behavior_sessions:
        updated = behavior_session.model_copy(
            update={
                "mouse_name": mouse_pk,
                "instrument": instrument_pk,
                "trainers": trainer_pks,
            },
        )
        try:
            validated = SlimsBehaviorSessionContentEvent.model_validate(
                updated, from_attributes=True)
        except ValidationError as e:
            logger.error(
                f"SLIMS data validation failed. Skipping write, {repr(e)}")
            continue
        added.append(client.add_model(validated))

    return added
