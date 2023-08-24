import os
from typing import List, Dict

from phenopackets import Phenopacket
from google.protobuf.json_format import MessageToJson
def map_phenopacket2json(phenopacket:Phenopacket) -> str:
    return MessageToJson(phenopacket)

def write_phenopacket2json_file(phenopacket: Phenopacket, path: str) -> None:
    json_str = map_phenopacket2json(phenopacket)
    out_path = os.path.join(path, phenopacket.id)
    with open(out_path, 'w') as fh:
        fh.write(json_str)

def write_phenopackets2json_file(phenopackets_list: List[Phenopacket], path:str) -> None:
    # Make sure output path exists
    os.makedirs(path, exist_ok=True)

    for phenopacket in phenopackets_list:
        write_phenopacket2json_file(phenopacket, path)
