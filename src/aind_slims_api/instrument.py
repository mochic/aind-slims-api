"""Contains a model for the mouse content, and a method for fetching it"""

import logging
from typing import Any

from pydantic import Field

from aind_slims_api.core import SlimsBaseModel, SlimsClient, SLIMSTABLES

logger = logging.getLogger()


class SlimsInstrument(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent"""

    name: str = Field(..., alias="nstr_name")
    pk: int = Field(..., alias="nstr_pk")
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
            Validated SlimsInstrument objects
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
