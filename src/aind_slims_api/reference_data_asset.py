import logging

from pydantic import (
    Field
)

from aind_slims_api.core import (
    SlimsClient, SlimsBaseModel, SLIMSTABLES,
)


logger = logging.getLogger()


class SlimsReferenceDataAsset(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent"""

    name: str = Field(..., alias="rdrc_name")
    pk: int = Field(..., alias="rdrc_pk")
    _slims_table = "ReferenceDataRecord"



def fetch_reference_data_asset(client: SlimsClient, asset_name: str) -> \
        list[SlimsReferenceDataAsset]:
    """Fetches reference data asset for a mouse with labtracks id {mouse_name}

    Examples
    --------
    >>> client = SlimsClient()
    >>> asset = fetch_reference_data_asset(client, "323_EPHYS1_OPTO_20240212")
    >>> rig_metadata_attachment = next(asset[0].resolve_attachments())
    >>> rig_metadata_attachment["rig_id"]
    '323_EPHYS1_OPTO_2024-02-12'

    Returns
    -------
    list:
        Validated SlimsReferenceDataAsset objects

    Notes
    -----
    - `asset_name` is used to filter the `rdrc_name` field in the
     `ReferenceDataRecord` table
    """
    validated, _ = client.fetch_models(
        SlimsReferenceDataAsset,
        rdrc_name=asset_name,
    )
    return validated


if __name__ == "__main__":
    import doctest
    import logging

    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod(
        optionflags=(
            doctest.IGNORE_EXCEPTION_DETAIL | doctest.NORMALIZE_WHITESPACE
        )
    )