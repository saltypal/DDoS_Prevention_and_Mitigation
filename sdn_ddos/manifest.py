"""Deterministic episode identities and reproducible paired intervention order."""
import hashlib
import json
import random


def episode_manifest(config):
    episodes = []
    for family in config['topology']['families']:
        for seed in config['main_experiment']['workload_seeds']:
            cells = [(label, band) for label in config['labels'] for band in config['main_experiment']['load_bands']]
            random.Random(seed).shuffle(cells)
            for label, band in cells:
                episodes.append(dict(episode_id=f"{family['id']}-{seed}-{label}-{band}",
                                     topology_id=family['id'], workload_seed=seed, label=label,
                                     load_band=band, experiment='main'))
    hop = config['hop_experiment']
    for seed in hop['workload_seeds']:
        for condition in hop['traffic_conditions']:
            payload = json.dumps([config['config_id'], seed, condition['scenario']], ensure_ascii=True,
                                 separators=(',', ':')).encode('utf-8')
            order_seed = int.from_bytes(hashlib.sha256(payload).digest()[:8], 'big')
            cells = [dict(cell) for cell in hop['initial_cell_order']]
            random.Random(order_seed).shuffle(cells)
            for cell in cells:
                identifier = f"T3-{seed}-{condition['scenario']}-{cell['path']}-{cell['propagation_mode']}"
                episodes.append(dict(episode_id=identifier, topology_id='T3', workload_seed=seed,
                                     label=condition['label'], scenario=condition['scenario'],
                                     load_band=hop['load_band'], experiment='hop', **cell))
    return episodes
