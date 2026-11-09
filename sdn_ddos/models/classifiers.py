from __future__ import annotations
import numpy as np
from scipy.special import expit

SPARK_FAMILIES = ('logistic', 'decision_tree', 'random_forest', 'gbt', 'gaussian_nb', 'linear_svm', 'mlp', 'fm')
PYTHON_FAMILIES = ('hist_gradient_boosting', 'xgboost', 'lightgbm', 'catboost')
FAMILIES = SPARK_FAMILIES + PYTHON_FAMILIES


def python_pipeline(family, contract, seed=42):
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.impute import SimpleImputer
    from sklearn.ensemble import HistGradientBoostingClassifier
    numeric = Pipeline([('impute', SimpleImputer(strategy='median', add_indicator=True, keep_empty_features=True))])
    categorical = Pipeline([('impute', SimpleImputer(strategy='constant', fill_value='__missing__')),
                            ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
    prep = ColumnTransformer([('numeric', numeric, contract['numeric']), ('categorical', categorical, contract['categorical'])])
    if family == 'hist_gradient_boosting':
        classifier = HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=15, l2_regularization=1, random_state=seed)
    elif family == 'xgboost':
        from xgboost import XGBClassifier
        classifier = XGBClassifier(n_estimators=120, max_depth=5, learning_rate=0.08, n_jobs=2, tree_method='hist', random_state=seed, eval_metric='logloss')
    elif family == 'lightgbm':
        from lightgbm import LGBMClassifier
        classifier = LGBMClassifier(n_estimators=120, num_leaves=15, n_jobs=2, random_state=seed, verbosity=-1)
    elif family == 'catboost':
        from catboost import CatBoostClassifier
        classifier = CatBoostClassifier(iterations=120, depth=5, thread_count=2, random_seed=seed, verbose=False, allow_writing_files=False)
    else:
        raise ValueError(family)
    return Pipeline([('preprocessing', prep), ('classifier', classifier)])


def spark_frame(spark, table, contract, labels=False):
    """Explicit schema avoids all-null type inference and pandas index/order assumptions."""
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
    columns = contract['numeric'] + contract['categorical']
    types = [DoubleType()] * len(contract['numeric']) + [StringType()] * len(contract['categorical'])
    if labels:
        columns = columns + ['target']
        types = types + [DoubleType()]
    schema = StructType([StructField('_index', LongType(), False)] + [StructField(c, t, True) for c, t in zip(columns, types)])
    records = []
    for index, values in enumerate(table[columns].itertuples(index=False, name=None)):
        row = [index]
        for value, data_type in zip(values, types):
            if isinstance(data_type, DoubleType):
                row.append(float(value) if value is not None and np.isfinite(float(value)) else None)
            else:
                row.append(str(value) if value is not None else '__missing__')
        records.append(tuple(row))
    return spark.createDataFrame(records, schema=schema)


def spark_pipeline(family, contract, seed=42):
    from pyspark.ml import Pipeline
    from pyspark.ml.feature import Imputer, StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler, SQLTransformer
    from pyspark.ml.classification import (LogisticRegression, DecisionTreeClassifier, RandomForestClassifier,
                                         GBTClassifier, NaiveBayes, LinearSVC, MultilayerPerceptronClassifier, FMClassifier)
    stages, assembled = [], []
    if contract['numeric']:
        imputed = [f'_n{i}' for i in range(len(contract['numeric']))]
        missing = [f'_missing{i}' for i in range(len(contract['numeric']))]
        statements = ', '.join(f'CASE WHEN `{c}` IS NULL THEN 1.0 ELSE 0.0 END AS {m}' for c, m in zip(contract['numeric'], missing))
        stages.append(SQLTransformer(statement='SELECT *, ' + statements + ' FROM __THIS__'))
        stages.append(Imputer(strategy='median', inputCols=contract['numeric'], outputCols=imputed))
        assembled.extend(imputed + missing)
    if contract['categorical']:
        indexed = [f'_c{i}' for i in range(len(contract['categorical']))]
        encoded = [f'_o{i}' for i in range(len(contract['categorical']))]
        for original, destination in zip(contract['categorical'], indexed):
            stages.append(StringIndexer(inputCol=original, outputCol=destination, handleInvalid='keep'))
        stages.append(OneHotEncoder(inputCols=indexed, outputCols=encoded, handleInvalid='keep'))
        assembled.extend(encoded)
    scaled = family in ('logistic', 'linear_svm', 'mlp', 'fm', 'gaussian_nb')
    stages.append(VectorAssembler(inputCols=assembled, outputCol='_features' if scaled else 'features'))
    if scaled:
        stages.append(StandardScaler(inputCol='_features', outputCol='features', withMean=False, withStd=True))
    constructors = {
        'logistic': lambda: LogisticRegression(labelCol='target', maxIter=80, regParam=0.05),
        'decision_tree': lambda: DecisionTreeClassifier(labelCol='target', maxDepth=6, seed=seed),
        'random_forest': lambda: RandomForestClassifier(labelCol='target', numTrees=80, maxDepth=7, seed=seed),
        'gbt': lambda: GBTClassifier(labelCol='target', maxIter=50, maxDepth=4, seed=seed),
        'gaussian_nb': lambda: NaiveBayes(labelCol='target', modelType='gaussian', smoothing=1),
        'linear_svm': lambda: LinearSVC(labelCol='target', maxIter=80, regParam=0.05),
        'fm': lambda: FMClassifier(labelCol='target', maxIter=50, factorSize=8, stepSize=0.01, seed=seed)}
    # MLP input width is resolved after fitting the training-only feature pipeline.
    return Pipeline(stages=stages), constructors.get(family)


def fit_spark(family, train, contract, spark, seed=42):
    from pyspark.ml import PipelineModel
    from pyspark.ml.classification import MultilayerPerceptronClassifier
    features, constructor = spark_pipeline(family, contract, seed)
    frame = spark_frame(spark, train, contract, labels=True)
    fitted = features.fit(frame)
    transformed = fitted.transform(frame)
    if family == 'mlp':
        width = len(transformed.select('features').first()[0])
        classifier = MultilayerPerceptronClassifier(labelCol='target', layers=[width, 32, 16, 2], maxIter=80, seed=seed, blockSize=128)
    else:
        classifier = constructor()
    result = classifier.fit(transformed)
    return PipelineModel(stages=fitted.stages + [result])


def predict_spark(model, table, contract, spark):
    from pyspark.ml.functions import vector_to_array
    from pyspark.sql import functions as F
    output = model.transform(spark_frame(spark, table, contract))
    if 'probability' in output.columns:
        values = output.select('_index', vector_to_array('probability')[1].alias('score')).orderBy('_index').toPandas()['score'].to_numpy()
    else:
        margins = output.select('_index', vector_to_array('rawPrediction')[1].alias('score')).orderBy('_index').toPandas()['score'].to_numpy()
        values = expit(margins)  # Raw ranking score; independently calibrated before operational use.
    if len(values) != len(table) or not np.isfinite(values).all():
        raise RuntimeError('Invalid/misaligned Spark scores')
    return values
