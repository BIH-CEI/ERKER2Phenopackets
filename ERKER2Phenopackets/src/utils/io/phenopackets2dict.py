from phenopackets import Phenopacket
from google.protobuf.json_format import MessageToJson
from json import loads

from typing import List, Union, Dict, Any


def phenopacket2dict(phenopacket: Phenopacket) -> Dict:
    return loads(MessageToJson(phenopacket))
