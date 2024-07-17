"""Contains a model for the mouse content, and a method for fetching it"""

import logging
from typing import Annotated, ClassVar

from pydantic import Field, BeforeValidator

from aind_slims_api.core import SlimsBaseModel, UnitSpec

logger = logging.getLogger()


class SlimsMouseContent(SlimsBaseModel):
    """Model for an instance of the Mouse ContentType
    
    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> client = SlimsClient()
    >>> mouse = client.fetch_model(SlimsMouseContent, barcode="00000000")
    """

    baseline_weight_g: Annotated[float | None, UnitSpec("g")] = Field(
        ..., alias="cntn_cf_baselineWeight"
    )
    point_of_contact: str | None = Field(..., alias="cntn_cf_scientificPointOfContact")
    water_restricted: Annotated[bool, BeforeValidator(lambda x: x or False)] = Field(
        ..., alias="cntn_cf_waterRestricted"
    )
    barcode: str = Field(..., alias="cntn_barCode")
    pk: int = Field(..., alias="cntn_pk")

    _slims_table = "Content"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "cntp_name": "Mouse",
    }

    # TODO: Include other helpful fields (genotype, gender...)

    # pk: callable
    # cntn_fk_category: SlimsColumn
    # cntn_fk_contentType: SlimsColumn
    # cntn_barCode: SlimsColumn
    # cntn_id: SlimsColumn
    # cntn_cf_contactPerson: SlimsColumn
    # cntn_status: SlimsColumn
    # cntn_fk_status: SlimsColumn
    # cntn_fk_user: SlimsColumn
    # cntn_cf_fk_fundingCode: SlimsColumn
    # cntn_cf_genotype: SlimsColumn
    # cntn_cf_labtracksId: SlimsColumn
    # cntn_cf_parentBarcode: SlimsColumn


if __name__ == "__main__":
    from aind_slims_api import testmod

    testmod()
