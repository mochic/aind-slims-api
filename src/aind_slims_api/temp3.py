import os
import requests
from aind_slims_api import SlimsClient
from slims.criteria import conjunction, equals


client = SlimsClient()

criteria = conjunction()
criteria.add(
    equals("rdrc_name", "323_EPHYS1_OPTO_20240212")
)
records = client.db.fetch(
    "ReferenceDataRecord",
    criteria=criteria,
)
attachments = records[0].attachments()
for link_d in attachments[0].json_entity["links"]:
    if link_d["rel"] == "contents":
        link = link_d["href"]
r = requests.get(
    link,
    auth=(os.getenv("SLIMS_USERNAME"), os.getenv("SLIMS_PASSWORD")),
)
print(r.json())
