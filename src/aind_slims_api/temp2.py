import json
import os
import requests
import pathlib
from aind_slims_api import SlimsClient
from slims.criteria import Criterion, conjunction, equals


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
print(dir(attachments[0]))
pathlib.Path("records-att.json").write_text(
    json.dumps(attachments[0].json_entity, indent=2, sort_keys=True)
)
pathlib.Path("records-ref.json").write_text(
    json.dumps(records[0].json_entity, indent=2, sort_keys=True)
)
# print(records.json_entity)
for link_d in attachments[0].json_entity["links"]:
    if link_d["rel"] == "contents":
        link = link_d["href"]
r = requests.get(
    link,
    auth=(os.getenv("SLIMS_USERNAME"), os.getenv("SLIMS_PASSWORD")),
)
# print(r.json())
# pk = attachments[0].pk()
# print(pk)
# criteria_2 = conjunction()
# criteria_2.add(
#     equals("cntn_pk", pk)
# )
# records = client.db.fetch(
#     "Content",
#     criteria=criteria_2,
# )
# print(records)