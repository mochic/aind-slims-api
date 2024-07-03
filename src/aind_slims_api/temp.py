import os
import json
import pathlib
import requests

url = "https://aind-test.us.slims.agilent.com/slimsrest"
username = os.getenv("SLIMS_USERNAME")
password = os.getenv("SLIMS_PASSWORD")
instrument_id = "323_EPHYS1_OPTO_20240212"

resolved_url = f"{url}/rest/ReferenceDataRecord/advanced"
print(resolved_url)
first_response = requests.get(
  resolved_url,
  auth=(username, password),
  json={'sortBy': None, 'startRow': None, 'endRow': None, 'criteria': {'fieldName': 'rdrc_name', 'operator': 'equals', 'value': instrument_id}},
)

first_entity = first_response.json()["entities"][0]
pathlib.Path("first.json").write_text(json.dumps(first_entity, indent=4, sort_keys=True))
resolved_url = f"{url}/rest/attachment/{first_entity['tableName']}/{first_entity['pk']}"
print(resolved_url)
second_response = requests.get(
  f"{url}/rest/attachment/{first_entity['tableName']}/{first_entity['pk']}",
  auth=(username, password),
)

second_entity = second_response.json().get("entities")[0]
pathlib.Path("second.json").write_text(json.dumps(second_entity, indent=4, sort_keys=True))
resolved_url = f"{url}/rest/repo/{second_entity['pk']}"
print(resolved_url)
third_response = requests.get(
  resolved_url,
  auth=(username, password),
)

instrument_or_rig = third_response.json()
pathlib.Path("third.json").write_text(json.dumps(instrument_or_rig, indent=4, sort_keys=True))