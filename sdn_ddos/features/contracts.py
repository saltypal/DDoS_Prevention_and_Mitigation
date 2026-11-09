NF_EXCLUDED = {'FLOW_START_MILLISECONDS', 'FLOW_END_MILLISECONDS', 'IPV4_SRC_ADDR', 'IPV4_DST_ADDR',
               'L4_SRC_PORT', 'L4_DST_PORT', 'Label', 'Attack', 'DNS_QUERY_ID'}
LAN_EXCLUDED = {'src_MAC', 'dst_MAC', 'src_IP', 'dst_IP', 'subflow_id', 'timestamp_1', 'timestamp_2', 'label', 'new_mac_ratio'}
NF_CATEGORICAL = {'PROTOCOL', 'L7_PROTO', 'ICMP_TYPE', 'ICMP_IPV4_TYPE', 'DNS_QUERY_TYPE', 'FTP_COMMAND_RET_CODE'}
LAN_CATEGORICAL = {'last_layer', 'eth_type', 'arp_opcode', 'OFpredominant_type'}
METADATA = {'source', 'topology', 'source_ordinal', 'source_file_hash', 'row_id'}
LABELS = {'ton': {'benign', 'scanning', 'dos', 'injection', 'ddos', 'password', 'xss', 'ransomware', 'backdoor', 'mitm'},
          'bot': {'benign', 'ddos', 'dos', 'reconnaissance', 'theft'},
          'lan': {'normal', 'ddos', 'injection', 'linkfab', 'hijack', 'portscan'}}


def feature_contract(source, columns):
    excluded = NF_EXCLUDED if source in ('ton', 'bot') else LAN_EXCLUDED
    categories = NF_CATEGORICAL if source in ('ton', 'bot') else LAN_CATEGORICAL
    predictors = sorted(set(columns) - excluded - METADATA)
    return {'source': source, 'numeric': [c for c in predictors if c not in categories],
            'categorical': [c for c in predictors if c in categories], 'excluded': sorted(excluded),
            'observation': 'completed NetFlow record' if source != 'lan' else 'creator LAN subflow record',
            'cross_source': 'NF-v3 only; LAN common contract unverified',
            'new_mac_ratio': 'excluded pending creator implementation audit'}
