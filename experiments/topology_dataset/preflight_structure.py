"""Validate actual Mininet graph construction without starting services."""
from sdn_ddos.topology import build_topology, load_config
from sdn_ddos.manifest import episode_manifest

config = load_config()
episodes = episode_manifest(config)
assert len(episodes) == 348
assert len({item['episode_id'] for item in episodes}) == 348
assert episodes == episode_manifest(config)
for family in config['topology']['families']:
    graph = build_topology(family['id'], config)
    assert len(graph.switches()) == 7
    assert len(graph.hosts()) == 16
    assert len(graph.links()) == len(family['edges']) + 16
    print(f"{family['id']}: 7 switches, 16 hosts, {len(graph.links())} links", flush=True)
print('348 unique deterministic episodes; Mininet construction passed.', flush=True)
