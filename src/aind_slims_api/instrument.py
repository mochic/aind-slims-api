"""Contains a model for the mouse content, and a method for fetching it"""

import logging
from typing import Any
from datetime import datetime

from pydantic import Field, ValidationError, field_serializer

from aind_slims_api.core import SlimsBaseModel, SlimsClient, SLIMSTABLES
from aind_slims_api.mouse import fetch_mouse_content, SlimsMouseContent
from aind_slims_api.user import fetch_user

logger = logging.getLogger()


class SlimsInstrument(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent"""

    name: str = Field(..., serialization_alias="nstr_name")
    pk: int = Field(..., serialization_alias="nstr_pk")
    _slims_table: SLIMSTABLES = "Instrument"

    # todo add more useful fields


def fetch_instrument_content(
    client: SlimsClient,
    instrument_name: str,
) -> SlimsInstrument | dict[str, Any] | None:
    """Fetches behavior sessions for a mouse with labtracks id {mouse_name}

    Returns
    -------
    tuple:
        list:
            Validated SlimsBehaviorSessionContentEvent objects
        list:
            Dictionaries representations of objects that failed validation

    Notes
    -----
    - Todo: add partial name match or some other type of filtering
    """
    validated, unvalidated = client.fetch_models(
        SlimsInstrument,
        nstr_name=instrument_name,
    )
    if len(validated) > 0:
        instrument_details = validated[0]
        if len(validated) > 1:
            logger.warning(
                f"Warning, Multiple instruments in SLIMS with name {instrument_name}, "
                f"using pk={instrument_details.pk}"
            )
            return instrument_details
    else:
        if len(unvalidated) > 0:
            logger.warning(
                f"Warning, Multiple instruments in SLIMS with name {instrument_name}, "
                f"using pk={unvalidated[0]['pk']}"
            )
            return unvalidated[0]
        
    return None


if __name__ == "__main__":
    import os
    logger.setLevel(logging.DEBUG)
    client = SlimsClient(
        username=os.getenv("SLIMS_USERNAME"),
        password=os.getenv("SLIMS_PASSWORD"),
    )
    ret = client.fetch(
        "Instrument",
        nstr_name="323_EPHYS1_OPTO",
    )
    import json

    # ret = fetch_instrument_content(
    #     client,
    #     "323_EPHYS1_OPTO_20240212",
    # )
    print([
        item.nstr_name.value for item in ret
    ])
