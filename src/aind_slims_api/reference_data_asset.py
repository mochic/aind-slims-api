import os
import logging
import requests

from pydantic import (
    Field, ValidationError, ValidationInfo, BaseModel, field_validator
)
from typing import Callable

from aind_slims_api.core import (
    SlimsClient, SlimsBaseModel, SLIMSTABLES,
)
from slims.criteria import conjunction, equals


logger = logging.getLogger()


class SlimsLink(BaseModel):

    rel: str
    href: str


class SlimsReferenceDataAssetAttachment(SlimsBaseModel):

    name: str = Field(..., alias="rdra_name")
    pk: int = Field(..., alias="attm_pk")
    links: list[SlimsLink] = Field(..., alias="links")
    _slims_table: SLIMSTABLES = "ReferenceDataRecordAttachment"

    # @field_validator("links", mode="before")
    # @classmethod
    # def _validate(cls, value: ]):
    #     if isinstance(value, list):
    #         print(type(value[0]))
    #     return super()._validate(value, info)

    def fetch_content(
        self,
        session: requests.Session,
    ) -> dict | None:
        for link in self.links:
            if link.rel == "contents":
                break
        else:
            logger.error("No link found for content")
            return None
        logger.debug(f"Resolved link: {link}")
        response = session.get(link.href)
        response.raise_for_status()
        return response.json()

    # todo add more useful fields


class SlimsReferenceDataAsset(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent"""

    name: str = Field(..., alias="rdrc_name")
    pk: int = Field(..., alias="rdrc_pk")
    attachments: list[SlimsReferenceDataAssetAttachment] = Field(...,)
    _slims_table: SLIMSTABLES = "ReferenceDataRecord"

    @field_validator("attachments", mode="before")
    @classmethod
    def _validate(cls, value) -> list[SlimsReferenceDataAssetAttachment]:
        # attachment_records = value()
        # print(dir(attachment_records[0]))
        return [
            SlimsReferenceDataAssetAttachment.model_validate(attachment)
            for attachment in value()
        ]
    # def attachments(self) -> list[SlimsReferenceDataAssetAttachment]:
    #     validated = []
    #     for attachment in self.json_entity["attachments"]:
    #         try:
    #             validated.append(
    #                 SlimsReferenceDataAssetAttachment(**attachment))
    #         except ValidationError:
    #             logger.error(
    #                 f"Failed to validate attachment: {attachment}")
    #     return validated

    # todo add more useful fields



def fetch_reference_data_asset(client: SlimsClient, asset_name: str) -> \
        list[SlimsReferenceDataAsset]:
    """Fetches reference data asset for a mouse with labtracks id {mouse_name}

    Examples
    --------
    >>> client = SlimsClient()
    >>> asset = fetch_reference_data_asset(client, "323_EPHYS1_OPTO_20240212")

    Returns
    -------
    list:
        Validated SlimsReferenceDataAsset objects

    Notes
    -----
    """
    validated, _ = client.fetch_models(
        SlimsReferenceDataAsset,
        rdrc_name=asset_name,
    )
    return validated
    # attachments = records[0].attachments()
    # for link_d in attachments[0].json_entity["links"]:
    #     if link_d["rel"] == "contents":
    #         link = link_d["href"]
    # r = requests.get(
    #     link,
    #     auth=(os.getenv("SLIMS_USERNAME"), os.getenv("SLIMS_PASSWORD")),
    # )
    # print(r.json())


if __name__ == "__main__":
    import doctest
    import dotenv
    import logging
    logging.basicConfig(level=logging.DEBUG)
    dotenv.load_dotenv()
    doctest.testmod(
        optionflags=(
            doctest.IGNORE_EXCEPTION_DETAIL | doctest.NORMALIZE_WHITESPACE
        )
    )