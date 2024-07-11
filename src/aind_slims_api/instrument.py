"""Contains a model for the instrument content, and a method for fetching it"""
import os
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
    instrument_id: str | None = None,
) -> SlimsInstrument | dict[str, Any] | None:
    """Fetches behavior sessions for a mouse with labtracks id {mouse_name}

    Examples
    --------
    >>> client = SlimsClient()
    >>> instrument = fetch_instrument_content(client, "323_EPHYS1_OPTO")
    >>> fetch_instrument_content(client, "323_EPHYS1_OPTO_20240212", "323_EPHYS1_OPTO_20240212")

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
    - TODO: reconsider this pattern, consider just returning all records or
     having number returned be a parameter or setting
    """
    if instrument_id is not None:
        validated, unvalidated = client.fetch_models(
            SlimsInstrument,
            rig_id=instrument_id,
        )
    else:
        validated, unvalidated = client.fetch_models(
            SlimsInstrument,
            nstr_name=instrument_name,
        )
    if len(validated) > 0:
        validated_details = validated[0]
        if len(validated) > 1:
            logger.warning(
                f"Warning, Multiple instruments in SLIMS with name {instrument_name}, "
                f"using pk={validated_details.pk}"
            )
        return validated_details
    else:
        if len(unvalidated) > 0:
            unvalidated_details = unvalidated[0]
            if len(unvalidated) > 1:
                logger.warning(
                    "Warning, Multiple instruments in SLIMS with name "
                    f"{instrument_name}, "
                    f"using pk={unvalidated_details['pk']}"
                )
            return unvalidated[0]

    return None


if __name__ == "__main__":
    import doctest
    import logging

    logging.basicConfig(level=logging.DEBUG)

    doctest.testmod(
        optionflags=(
            doctest.IGNORE_EXCEPTION_DETAIL | doctest.NORMALIZE_WHITESPACE
        )
    )
