"""Algebraic source-native derivatives with explicit units and undefined denominators."""
def derive(data, source, contract):
    from pyspark.sql import functions as F
    registry = []
    if source in ('ton', 'bot'):
        formulas = {
            'derived_total_bytes': (F.col('IN_BYTES') + F.col('OUT_BYTES'), 'IN_BYTES + OUT_BYTES', 'bytes'),
            'derived_total_packets': (F.col('IN_PKTS') + F.col('OUT_PKTS'), 'IN_PKTS + OUT_PKTS', 'packets')}
        bytes_in, bytes_out, packets = F.col('IN_BYTES'), F.col('OUT_BYTES'), F.col('IN_PKTS') + F.col('OUT_PKTS')
    else:
        formulas = {}
        bytes_in, bytes_out, packets = F.col('fw_bytes'), F.col('bk_bytes'), F.col('packets')
    denominator = bytes_in + bytes_out
    formulas.update({
        'derived_directional_byte_balance': (F.when(denominator > 0, (bytes_in - bytes_out) / denominator),
                                            '(direction1_bytes-direction2_bytes)/(direction1_bytes+direction2_bytes)', 'dimensionless'),
        'derived_mean_bytes_per_packet': (F.when(packets > 0, (bytes_in + bytes_out) / packets),
                                          '(direction1_bytes+direction2_bytes)/recorded_packet_count', 'bytes/packet')})
    for name, (expression, formula, unit) in formulas.items():
        data = data.withColumn(name, expression.cast('double'))
        contract['numeric'].append(name)
        registry.append({'feature': name, 'formula': formula, 'unit': unit,
                         'undefined': 'missing when operands missing or denominator<=0',
                         'scope': 'source-native record; no cross-network conservation claim'})
    contract['derivatives'] = registry
    return data, contract
