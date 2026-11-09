import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sdn_ddos.runtime.run import write_json


def profile(data, source, contract, config, run):
    from pyspark.sql import functions as F
    counts = data.groupBy('split', 'attack_family').count().toPandas()
    counts.to_csv(run.root / 'reports' / f'{source}-class-counts.csv', index=False)
    # Full-table quality has already been audited; plots informing methodology exclude final tests.
    development = data.filter("split IN ('train','development')")
    n = development.count()
    cap = config.get('plot_rows', 20000)
    sample = development.sample(False, min(1.0, 1.2 * cap / max(n, 1)), seed=42).limit(cap).toPandas()
    sample.drop(columns=contract['numeric'] + contract['categorical'], errors='ignore').to_parquet(run.root / 'reports' / f'{source}-plot-row-manifest.parquet', index=False)
    if sample.empty:
        write_json(run.root / 'reports' / f'{source}-eda-unavailable.json', {'reason': 'No retained development observations', 'rows': n})
        return
    figures = run.root / 'figures' / source
    figures.mkdir()
    def save(name, title):
        plt.title(title)
        plt.tight_layout()
        plt.savefig(figures / (name + '.png'), dpi=130)
        plt.close()
        print('FIGURE', figures / (name + '.png'), flush=True)
    plt.figure(figsize=(10, 4))
    counts.pivot(index='attack_family', columns='split', values='count').fillna(0).plot.bar(ax=plt.gca(), logy=True)
    save('01-class-distribution', f'{source}: recorded labels and partitions (descriptive only)')
    numeric = sample[contract['numeric']].astype(float)
    plt.figure(figsize=(9, 5))
    numeric.isna().mean().sort_values().tail(15).plot.barh(ax=plt.gca())
    save('02-missingness', f'{source}: sampled development missingness')
    variability = numeric.nunique().sort_values(ascending=False)
    selected = list(variability[variability > 1].index[:4])
    if not selected:
        write_json(run.root / 'reports' / f'{source}-distribution-unavailable.json', {'reason': 'No variable numeric development features'})
        return
    plt.figure(figsize=(10, 5))
    for column in selected:
        values = numeric[column].dropna()
        plt.hist(np.sign(values) * np.log1p(np.abs(values)), bins=50, alpha=0.4, density=True, label=column)
    plt.legend(fontsize=7)
    save('03-distributions', f'{source}: signed-log display; raw measurements unchanged')
    plt.figure(figsize=(10, 8))
    columns = list(variability[variability > 1].index[:12])
    corr = numeric[columns].corr(method='spearman')
    plt.imshow(corr, vmin=-1, vmax=1, cmap='coolwarm')
    plt.colorbar()
    plt.xticks(range(len(columns)), columns, rotation=90, fontsize=7)
    plt.yticks(range(len(columns)), columns, fontsize=7)
    save('04-correlation', f'{source}: development sample Spearman correlations')
    column = selected[0]
    plt.figure(figsize=(9, 5))
    for family, group in sample.groupby('attack_family'):
        values = np.sort(group[column].astype(float).dropna())
        if len(values):
            plt.plot(np.sign(values) * np.log1p(np.abs(values)), np.arange(1, len(values) + 1) / len(values), label=family)
    plt.legend(fontsize=7)
    save('05-family-ecdf', f'{source}: {column} by original family; development sample')
    plt.figure(figsize=(10, 4))
    sample.groupby(['topology', 'attack_family']).size().unstack(fill_value=0).plot.bar(stacked=True, ax=plt.gca())
    save('06-topology', f'{source}: development sample by topology/provenance')
    write_json(run.root / 'reports' / f'{source}-eda-scope.json', {'development_rows': n, 'sample_rows': len(sample),
               'seed': 42, 'final_test_used_for_feature_selection': False, 'sampling': 'Bernoulli then capped; not class-stratified'})
