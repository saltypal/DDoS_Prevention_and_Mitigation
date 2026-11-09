"""Small behavioral checks; synthetic fixtures test the auditor, not IDS accuracy."""
from pathlib import Path
import contextlib
import importlib.util
import io
import json
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("builder", HERE / "build_investigation_notebook.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

with tempfile.TemporaryDirectory(prefix="audit-fixture-", dir=HERE / "runs") as temporary:
    root = Path(temporary)
    setup = builder.setup.replace("__RUN_ID__", repr("fixture")).replace("__SOURCE_SNAPSHOT__", repr("fixture-only"))
    setup = setup.replace("'/kaggle/working/experiments/public_dataset_la/runs'", repr(str(root / "output")))
    setup = setup.replace("'/kaggle/temp/public_dataset_investigation'", repr(str(root / "cache")))
    setup = setup.replace("'/kaggle/working'", repr(str(root)))
    ns = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(setup, "setup-fixture", "exec"), ns)
        exec(compile(builder.profiler, "profiler-fixture", "exec"), ns)
    np, pd = ns["np"], ns["pd"]
    hashes = pd.util.hash_pandas_object(pd.Series(np.arange(10_000)), index=False).to_numpy()
    sketch = ns["UniqueSketch"]()
    sketch.add(np.tile(hashes, 3))
    assert abs(sketch.estimate() - 10_000) / 10_000 < 0.04
    path = root / "tiny.csv"
    pd.DataFrame({"x": [1, 1, 2, 3, 4, 5], "rate": [2, 2, np.inf, np.nan, 7, 8],
                  "IPV4_SRC_ADDR": ["a", "b", "c", "d", "e", "f"],
                  "FLOW_START_MILLISECONDS": [1700000000000] * 6,
                  "Label": ["Normal", "DDoS", "DDoS", "Normal", "Normal", "DoS"]}).to_csv(path, index=False)
    ns["CHUNK_ROWS"] = 2
    with contextlib.redirect_stdout(io.StringIO()):
        report = ns["profile"]({"path": str(path), "candidate": "fixture"}, 1)
    assert report["rows_scanned"] == 6
    assert report["labels"] == {"Normal": 3, "DDoS": 2, "DoS": 1}
    assert "IPV4_SRC_ADDR" in report["excluded_predictors"]
    assert "FLOW_START_MILLISECONDS" in report["excluded_predictors"]
    for identifier in ['src_MAC', 'dst_MAC', 'subflow_id', 'activity', 'source_row']:
        assert ns['excluded_identifier'](identifier), identifier
    assert report["sample_conflicting_feature_hash_groups"] == 1
    details = json.loads((Path(report["report_directory"]) / "column_details.json").read_text())
    assert details["rate"]["missing"] == 1 and details["rate"]["nonfinite"] == 1
    assert details["x"]["mean"] == 16/6
    assert json.loads((Path(report["report_directory"]) / "day_label_counts.json").read_text())
    assert (Path(report["report_directory"]) / "audit_sample.csv").exists()
    sample_columns = pd.read_csv(Path(report["report_directory"]) / "audit_sample.csv").columns
    assert "IPV4_SRC_ADDR" not in sample_columns
    empty = root / "empty.csv"
    empty.write_text("x,Label\n")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            ns["profile"]({"path": str(empty), "candidate": "fixture"}, 2)
    except ValueError as exc:
        assert "Empty" in str(exc)
    else:
        raise AssertionError("Empty input must fail explicitly")

print("PASS: HLL reference tolerance, chunk coverage, label counts, missing/nonfinite values,")
print("identifier exclusion, conflicting-feature candidates, timestamps, output persistence and empty-input failure.")
