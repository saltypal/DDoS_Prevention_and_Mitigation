"""Presentation views over verified upstream artifacts, never fabricated results."""
import json
from pathlib import Path
import pandas as pd


def one_artifact(root, relative):
    hits = list(Path(root).rglob(relative))
    if len(hits) != 1:
        raise ValueError(f'Attach one version-specific upstream output containing {relative}; found {hits}')
    return hits[0]


def show_la1(source, root='/kaggle/input'):
    from IPython.display import display, Markdown, Image
    manifest_path = one_artifact(root, f'manifests/{source}-prepared.json')
    manifest = json.loads(manifest_path.read_text())
    if manifest['scope'] != 'full':
        raise ValueError('LA1 final presentation requires full-source artifacts, not prefix smoke')
    run = manifest_path.parent.parent
    display(Markdown(f'## Verified input\nSource **{source}**; observed rows **{manifest["rows"]:,}**. Input SHA256: `{manifest["input_sha256"]}`.'))
    for suffix in ('inputs', 'features', 'split-policy'):
        path = run / 'contracts' / f'{source}-{suffix}.json'
        display(Markdown(f'### {suffix}'))
        print(path.read_text())
    counts = pd.DataFrame(json.loads((run / 'reports' / f'{source}-split-counts.json').read_text()))
    display(counts)
    retained = counts[counts['split'].isin(['train','development','test'])]['count'].sum()
    display(Markdown(f'**Observed preprocessing inference:** {int(retained):,} observations remain in evaluation partitions; '
                     f'{manifest["rows"]-int(retained):,} are retained as quarantined observations. '
                     'These exclusions protect the declared split protocol and may change the evaluated population; inspect family counts.'))
    scope = json.loads((run / 'reports' / f'{source}-eda-scope.json').read_text())
    display(Markdown(f'Plots use **{scope["sample_rows"]:,}** sampled training/development rows unless marked full-table. '
                     'Final-test distributions were not used to choose features.'))
    for figure in sorted((run / 'figures' / source).glob('*.png')):
        display(Markdown('### ' + figure.stem.replace('-', ' ')))
        display(Image(filename=str(figure)))
    display(Markdown('Imputation, vocabulary fitting and scaling are fitted by the model modules on training rows only. '
                     'OOF models refit those transformations within each fold. This data artifact contains sanitized measurements, not globally fitted model vectors.'))


def show_la2(condition, root='/kaggle/input'):
    from IPython.display import display, Markdown
    import plotly.express as px
    path = one_artifact(root, 'reports/benchmark.json')
    records = [r for r in json.loads(path.read_text()) if r['condition'] == condition]
    if not records:
        raise ValueError(f'No executed benchmark for {condition}')
    rows = []
    for record in records:
        rows.append(dict(family=record['family'],status=record['status'],seconds=record.get('seconds'),
                         **record.get('development_metrics', {})))
    table = pd.DataFrame(rows)
    display(Markdown(f'## {condition}: executed classifier comparison\nThese are development results. Failures remain visible.'))
    display(table.drop(columns=['families'],errors='ignore'))
    successful = table[table['status']=='complete'].sort_values('average_precision',ascending=False)
    if successful.empty:
        display(Markdown('No successful classifiers: inspect fit logs before interpreting detection performance.'))
        return
    for metric in ['average_precision','recall','precision','f1','mcc','benign_fpr','seconds']:
        px.bar(successful,x='family',y=metric,title=f'{condition}: development {metric}').show()
    for _, row in successful.head(3).iterrows():
        display(Markdown(f'### {row["family"]}\nAt the diagnostic threshold {row["threshold"]:.3f}, '
                         f'DDoS recall={row["recall"]:.4f}, precision={row["precision"]:.4f}, '
                         f'F1={row["f1"]:.4f}, MCC={row["mcc"]:.4f}. '
                         f'Confusion counts: TP={int(row["tp"])}, FP={int(row["fp"])}, FN={int(row["fn"])}, TN={int(row["tn"])}. '
                         f'Fit-process wall time={row["seconds"]:.1f}s. '
                         'Compare benign false positives and other-attack family errors before selecting this model. '
                         'These scores do not establish final-test or unseen-source performance.'))
        family_record = next(r for r in records if r['family']==row['family'])
        display(pd.DataFrame(family_record['development_metrics']['families']).T)
    for filename in ('ensemble-development.json','moe-development.json'):
        hits = list(Path(root).rglob('reports/'+filename))
        if len(hits)==1:
            if filename == 'moe-development.json' and condition == 'lan':
                display(Markdown('**NF domain MoE does not include LAN; no common feature contract has been validated.**'))
                continue
            results = json.loads(hits[0].read_text())
            display(Markdown(f'## {filename}: separately calibrated combination results'))
            display(pd.DataFrame([r for r in results if r.get('condition',condition)==condition]))
        elif len(hits)>1:
            raise ValueError(f'Multiple {filename} versions; attach the intended run only')
        else:
            display(Markdown(f'**{filename}: no executed artifact attached yet.**'))
