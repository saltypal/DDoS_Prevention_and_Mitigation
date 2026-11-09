"""Construct the versioned graphs without importing Mininet on Windows."""
import json
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / 'experiments/topology_dataset/configs/dataset_v1.json'


def load_config(path=DEFAULT_CONFIG):
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream)


def build_topology(family_id, config=None):
    from mininet.topo import Topo
    config = config or load_config()
    families = {item['id']: item for item in config['topology']['families']}
    if family_id not in families:
        raise ValueError(f'Unknown topology {family_id}; choose from {list(families)}')
    topology = Topo()
    for index, switch in enumerate(config['topology']['switch_ids'], 1):
        topology.addSwitch(switch, dpid=f'{index:016x}', protocols='OpenFlow13', failMode='secure')
    links = config['links']
    for left, right in families[family_id]['edges']:
        topology.addLink(left, right, bw=links['requested_bottleneck_mbit_s'] * links['transit_capacity_multiplier'],
                         delay=f"{links['main_inter_switch_one_way_delay_ms']}ms")
    for anchor_index, anchor in enumerate(config['topology']['observation_anchors'], 1):
        for host_index in range(1, config['topology']['hosts_per_anchor'] + 1):
            name = f'h{anchor_index}{host_index}'
            topology.addHost(name, ip=f'10.77.{anchor_index}.{host_index}/16')
            topology.addLink(name, anchor,
                             bw=links['requested_bottleneck_mbit_s'] * links['minimum_other_access_capacity_multiplier'],
                             delay=f"{links['host_access_delay_ms']}ms")
    return topology
