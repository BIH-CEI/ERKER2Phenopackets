import os
from typing import List

from phenopackets import Phenopacket
from google.protobuf.json_format import MessageToJson


def _map_phenopacket2json_str(phenopacket: Phenopacket) -> str:
    return MessageToJson(phenopacket)


def write_phenopacket2json_file(phenopacket: Phenopacket, out_dr: str) -> None:
    json_str = _map_phenopacket2json_str(phenopacket)
    out_path = os.path.join(out_dr, (phenopacket.id + '.json'))
    with open(out_path, 'w') as fh:
        fh.write(json_str)
        print(f'Successfully wrote phenopacket to JSON {out_dr}')


def write_phenopackets2json_files(
        phenopackets_list: List[Phenopacket], out_dir: str) -> None:
    """Writes a list of phenopackets to JSON files.

    :param phenopackets_list: The list of phenopackets.
    :type phenopackets_list: List[Phenopacket]
    :param out_dir: The output directory.
    :type out_dir: str
    """
    # Make sure output out_dr exists.
    os.makedirs(out_dir, exist_ok=True)

    for phenopacket in phenopackets_list:
        write_phenopacket2json_file(phenopacket, out_dir)

    print(f'Wrote {len(phenopackets_list)} phenopackets to JSON in {out_dir}')