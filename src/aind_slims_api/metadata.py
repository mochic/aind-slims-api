from pydantic import Field
from typing import Any, Generator
from aind_slims_api.core import SlimsBaseModel, SlimsClient, SLIMSTABLES


# class MetadataAttachment(SlimsBaseModel):

#     pk = Field(..., alias="attm_pk")


class SlimsRigReferenceDataAsset(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent"""

    name: str = Field(..., alias="rdrc_name")
    pk: int = Field(..., alias="rdrc_pk")
    _slims_table = "ReferenceDataRecord"


# def fetch_metadata_attachments(
#     client: SlimsClient,
#     name: str,
# ) -> Generator[MetadataAttachment, None, None]:
#     """Name of the reference data asset to fetch metadata attachments for.
#     """
#     validated, _ = client.fetch_models(
#         SlimsRigReferenceDataAsset,
#         rdrc_name=name,
#     )
#     for attachment in validated[0].attachments():  # second request to slims
#         yield MetadataAttachment.model_validate(attachment)


def fetch_rig_metadata_attachment_content(
    client: SlimsClient,
    rig_metadata_name: str | SlimsRigReferenceDataAsset,
) -> Generator[dict[str, Any], None, None]:
    validated, _ = client.fetch_models(
        SlimsRigReferenceDataAsset,
        rdrc_name=rig_metadata_name,
    )
    for ref_data_asset in validated:
        for attachment_content in ref_data_asset.resolve_attachments_content():
            yield attachment_content


if __name__ == "__main__":
    import doctest
    import logging

    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod(
        optionflags=(
            doctest.IGNORE_EXCEPTION_DETAIL | doctest.NORMALIZE_WHITESPACE
        )
    )
