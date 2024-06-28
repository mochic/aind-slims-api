"""Contains a model for the mouse content, and a method for fetching it"""

import logging
from typing import Any
from datetime import datetime

from pydantic import Field, ValidationError, field_serializer

from aind_slims_api.core import SlimsBaseModel, SlimsClient, SLIMSTABLES
from aind_slims_api.mouse import fetch_mouse_content, SlimsMouseContent
from aind_slims_api.user import fetch_user

logger = logging.getLogger()


class SlimsBehaviorSessionContentEvent(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent"""

    pk: int = Field(..., alias="cnvn_pk")
    mouse_name: int | None = Field(default=None, alias="cnvn_fk_content")  # used as reference to mouse
    notes: str = Field(..., alias="cnvn_cf_notes")
    task_stage: str = Field(..., alias="cnvn_cf_taskStage")
    instrument: int = Field(..., alias="cnvn_cf_fk_instrument")  # TODO: Check if we want to use str for this, Dynamic Choice
    trainer: list[int] = Field(..., alias="cnvn_cf_fk_trainer")  # TODO: Check if we want to use str for this, Dynamic Choice
    task: str = Field(..., alias="cnvn_cf_task")
    is_curriculum_suggestion: bool = Field(
        ..., alias="cnvn_cf_stageIsOnCurriculum")
    task_version: str = Field(..., alias="cnvn_cf_taskSchemaVersion")
    software_version: str | None = Field(
        default=None, alias="cnvn_cf_softwareVersion")
    date: datetime = Field(..., alias="cnvn_cf_scheduledDate")

    cnvn_fk_contentEventType: int = 10

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
    # mouse = fetch_mouse_content(client, mouse_name)
    # print(mouse.model_dump().keys())
    mouse_pk = _fetch_mouse_pk(client, mouse_name)
    logger.debug(f"Mouse pk: {mouse_pk}")
    if mouse_pk is None:
        return [], []
    
    # response = client.fetch(
    #     "ContentEvent",
    #     cnvt_name="Behavior Session",
    #     cnvn_fk_content=mouse.pk,
    # )
    # print(len(response))
    # import json
    # import pathlib
    # pathlib.Path("temp.json").write_text(json.dumps([r.json_entity for r in response]))
    # # print(dir(response[1]))
    # # print(response[1].cnvt_name.value)
    # # return
    # # for attr in dir(response[1]):
    # #     if attr.startswith("cn"):
    # #         print(attr)
    # #         print(f"{attr}: {getattr(response[0], attr).value}")
    # # return
    # # print([
    # #     item.cnvn_fk_contentEventType
    # #     for item in response
    # # ])
    # # response = client.fetch(
    # #     "ContentEvent",
    # #     cnvn_fk_content_type="cnvt_behavior_session",
    # #     cnvn_fk_content=mouse.pk,
    # # )

    # # print(len(response))
    # # print(dir(response[1]))
    # # print(mouse.barcode)
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

    added = []
    for behavior_session in behavior_sessions:
        updated = behavior_session.model_copy(
            update={"mouse_name": mouse_pk})
        try:
            validated = SlimsBehaviorSessionContentEvent.model_validate(updated)
        except ValidationError as e:
            logger.error(
                f"SLIMS data validation failed. Skipping write, {repr(e)}")
            continue
        added.append(client.add_model(validated))

    return added


if __name__ == "__main__":
    import os
    logger.setLevel(logging.DEBUG)
    client = SlimsClient(
        username=os.getenv("SLIMS_USERNAME"),
        password=os.getenv("SLIMS_PASSWORD"),
    )
    ret = fetch_behavior_session_content_events(
        client,
        mouse_name="00000000",
    )
    response = client.fetch(
        "Instrument",
    )
    print(response[0].pk())
    # raise Exception("bur")
    # print(ret)
    # print(fetch_user(client, "ClarkR"))
    write_behavior_session_content_events(
        client,
        "00000000",
        SlimsBehaviorSessionContentEvent(
            cnvn_cf_notes="Test",
            cnvn_cf_taskStage="Test",
            cnvn_cf_fk_instrument=1743,
            cnvn_cf_fk_trainer=[19],
            cnvn_cf_task="Test",
            cnvn_cf_stageIsOnCurriculum=True,
            cnvn_cf_taskSchemaVersion="Test",
            cnvn_cf_softwareVersion="Test",
            cnvn_cf_scheduledDate=datetime(2021, 1, 1),
        ),
    )
