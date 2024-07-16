"""Contains a model for the instrument content, and a method for fetching it"""

import logging

from pydantic import Field

from aind_slims_api.core import SlimsBaseModel, SLIMSTABLES

logger = logging.getLogger()


class SlimsInstrument(SlimsBaseModel):
    """Model for a SLIMS instrument record.

    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> client = SlimsClient()
    >>> instrument = client.fetch_model(SlimsInstrument, name="323_EPHYS1_OPTO")
    """

    name: str = Field(
        ...,
        alias="nstr_name",
        description="The name of the instrument",
    )
    pk: int = Field(..., alias="nstr_pk")
    _slims_table: SLIMSTABLES = "Instrument"

    # todo add more useful fields


if __name__ == "__main__":
    from aind_slims_api import testmod

    testmod()
