"""Build the approved Kaggle-only runtime capability preflight notebook."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK_DIR = Path(__file__).resolve().parent
RUN_ID = "kaggle-preflight-20261107T071002Z"
OWNER = "satyapaladugu"
SLUG = "sdn-ddos-topology-capture"
PROJECT = "DDoS_Prevention_and_Mitigation"

SNAPSHOT_FILES = [
    "experiments/topology_dataset/configs/dataset_v1.json",
    "sdn_ddos/topology.py",
    "sdn_ddos/manifest.py",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


source_hashes = {name: sha256_file(ROOT / name) for name in SNAPSHOT_FILES}
source_snapshot = hashlib.sha256(
    "\n".join(f"{name}:{source_hashes[name]}" for name in SNAPSHOT_FILES).encode("utf-8")
).hexdigest()
created_utc = datetime.now(timezone.utc).isoformat()

setup_code = f'''# Purpose: identify this Kaggle CPU runtime and persist run provenance.
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, os, platform, sys, time

RUN_ID = {RUN_ID!r}
PROJECT = {PROJECT!r}
NOTEBOOK_ID = {f"{OWNER}/{SLUG}"!r}
SOURCE_SNAPSHOT_SHA256 = {source_snapshot!r}
SOURCE_FILE_SHA256 = {source_hashes!r}
DESIGN_CONFIG_PATH = "experiments/topology_dataset/configs/dataset_v1.json"
REMOTE_ROOT = Path("/kaggle/working/experiments/topology_dataset/runs") / RUN_ID
REMOTE_ROOT.mkdir(parents=True, exist_ok=True)
(REMOTE_ROOT / "logs").mkdir(exist_ok=True)
(REMOTE_ROOT / "logs" / "cell_stdout.log").write_text("", encoding="utf-8")
(REMOTE_ROOT / "logs" / "command_results.jsonl").write_text("", encoding="utf-8")

started_utc = datetime.now(timezone.utc).isoformat()
started_monotonic = time.monotonic()
manifest = {{
    "run_id": RUN_ID,
    "notebook": NOTEBOOK_ID,
    "purpose": "Kaggle CPU hosted-runtime capability preflight only",
    "status": "running",
    "started_utc": started_utc,
    "source_snapshot_sha256": SOURCE_SNAPSHOT_SHA256,
    "design_config_sha256": SOURCE_FILE_SHA256[DESIGN_CONFIG_PATH],
    "remote_output_root": str(REMOTE_ROOT),
    "scope": {{"training": False, "full_capture": False, "topology_started": False, "network_mutations": False, "package_install": False}},
}}
(REMOTE_ROOT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")

def emit(message, payload=None):
    record = {{"utc": datetime.now(timezone.utc).isoformat(), "message": message, "data": payload or {{}}}}
    rendered = json.dumps(record, sort_keys=True)
    print(rendered, flush=True)
    with (REMOTE_ROOT / "logs" / "cell_stdout.log").open("a", encoding="utf-8") as log:
        log.write(rendered + "\\n")

def write_json(name, obj):
    path = REMOTE_ROOT / name
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    temp.replace(path)
    return path

emit("environment_probe_started", {{"run_id": RUN_ID, "output_root": str(REMOTE_ROOT), "python": sys.version.split()[0]}})
try:
    import importlib.metadata as metadata
    package_versions = {{}}
    for package in ("kagglehub", "mininet", "ryu", "eventlet", "pyarrow", "psutil", "numpy", "pandas"):
        try:
            package_versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            package_versions[package] = None
except Exception as exc:
    package_versions = {{"probe_error": type(exc).__name__}}

meminfo = {{}}
try:
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        if key in {{"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}}:
            meminfo[key] = value.strip()
except OSError as exc:
    meminfo = {{"error": type(exc).__name__}}

env = {{key: os.environ.get(key) for key in ("KAGGLE_KERNEL_RUN_TYPE", "KAGGLE_URL_BASE") if os.environ.get(key)}}
environment = {{
    "observed_utc": datetime.now(timezone.utc).isoformat(),
    "platform": platform.platform(),
    "system": platform.system(),
    "release": platform.release(),
    "machine": platform.machine(),
    "python_executable": sys.executable,
    "python_version": sys.version,
    "package_versions": package_versions,
    "cpu_count": os.cpu_count(),
    "memory_proc_meminfo": meminfo,
    "kaggle_environment_markers": env,
    "working_directory": os.getcwd(),
    "resolved_repository_path": str(Path.cwd()) if (Path.cwd() / "sdn_ddos").is_dir() and (Path.cwd() / DESIGN_CONFIG_PATH).is_file() else None,
    "repository_checkout_available": (Path.cwd() / "sdn_ddos").is_dir() and (Path.cwd() / DESIGN_CONFIG_PATH).is_file(),
    "output_root": str(REMOTE_ROOT),
}}
write_json("environment.json", environment)
write_json("provenance.json", {{
    "project": PROJECT,
    "notebook": NOTEBOOK_ID,
    "source_revision": "no_git_metadata; SHA-256 source snapshot",
    "source_snapshot_sha256": SOURCE_SNAPSHOT_SHA256,
    "source_files_sha256": SOURCE_FILE_SHA256,
    "design_config_path": DESIGN_CONFIG_PATH,
    "design_config_sha256": SOURCE_FILE_SHA256[DESIGN_CONFIG_PATH],
    "notebook_created_utc_local": {created_utc!r},
    "remote_run_id": RUN_ID,
}})
emit("environment_probe_complete", {{"environment_path": str(REMOTE_ROOT / "environment.json"), "provenance_path": str(REMOTE_ROOT / "provenance.json"), "elapsed_seconds": round(time.monotonic() - started_monotonic, 3)}})
'''

capability_code = '''# Purpose: probe runtime privileges and installed native-network tooling without changing networking.
import fcntl, json, os, platform, shutil, stat, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

probe_started = time.monotonic()
emit("capability_probe_started", {"output_root": str(REMOTE_ROOT), "network_mutations": False, "package_install": False})

def run_readonly(name, argv, timeout=8):
    started = time.monotonic()
    try:
        result = subprocess.run(argv, text=True, capture_output=True, timeout=timeout, check=False)
        record = {"name": name, "argv": argv, "returncode": result.returncode,
                  "stdout": result.stdout[-12000:], "stderr": result.stderr[-12000:],
                  "elapsed_seconds": round(time.monotonic() - started, 3)}
    except Exception as exc:
        record = {"name": name, "argv": argv, "exception": type(exc).__name__,
                  "message": str(exc)[:1000], "elapsed_seconds": round(time.monotonic() - started, 3)}
    with (REMOTE_ROOT / "logs" / "command_results.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps(record, sort_keys=True) + "\\n")
    emit("command_finished", {"name": name, "returncode": record.get("returncode"),
                               "exception": record.get("exception"), "elapsed_seconds": record["elapsed_seconds"],
                               "stdout_tail": record.get("stdout", "")[-700:],
                               "stderr_tail": record.get("stderr", "")[-700:]})
    return record

def status_caps():
    values = {}
    try:
        for line in Path("/proc/self/status").read_text().splitlines():
            if line.startswith(("CapEff:", "CapPrm:", "CapBnd:", "Uid:", "Gid:")):
                key, value = line.split(":", 1)
                values[key] = value.strip()
        for key in ("CapEff", "CapPrm", "CapBnd"):
            if key in values:
                mask = int(values[key], 16)
                values[key + "_named"] = {name: bool(mask & (1 << bit)) for name, bit in
                                           (("CAP_NET_ADMIN", 12), ("CAP_NET_RAW", 13), ("CAP_SYS_ADMIN", 21), ("CAP_SYS_MODULE", 16))}
    except Exception as exc:
        values["error"] = type(exc).__name__
    return values

commands = []
for name, argv in [
    ("identity", ["id"]),
    ("kernel", ["uname", "-a"]),
    ("virtualization", ["systemd-detect-virt"]),
    ("netns_clone", ["unshare", "-n", "--", "true"]),
    ("interfaces_readonly", ["ip", "-details", "link", "show"]),
    ("veth_syntax_only", ["ip", "link", "help", "type", "veth"]),
    ("ovs_readonly_status", ["ovs-vsctl", "--timeout=5", "show"]),
    ("ovs_readonly_datapaths", ["ovs-dpctl", "dump-dps"]),
    ("ovs_service_state", ["systemctl", "is-active", "openvswitch-switch"]),
    ("mininet_version", ["mn", "--version"]),
    ("qemu_x86_version", ["qemu-system-x86_64", "--version"]),
    ("qemu_arm_version", ["qemu-system-aarch64", "--version"]),
    ("kvm_device", ["ls", "-l", "/dev/kvm"]),
    ("tun_device", ["ls", "-l", "/dev/net/tun"]),
]:
    if shutil.which(argv[0]) or argv[0] in ("ls",):
        commands.append(run_readonly(name, argv))
    else:
        record = {"name": name, "argv": argv, "unavailable": True}
        commands.append(record)
        with (REMOTE_ROOT / "logs" / "command_results.jsonl").open("a", encoding="utf-8") as log:
            log.write(json.dumps(record, sort_keys=True) + "\\n")
        emit("command_unavailable", {"name": name, "executable": argv[0]})

paths = {path: {"exists": Path(path).exists(), "readable": os.access(path, os.R_OK),
                "writable": os.access(path, os.W_OK)} for path in
         ("/dev/net/tun", "/dev/kvm", "/sys/module/openvswitch", "/proc/self/ns/net", "/run/openvswitch", "/var/run/openvswitch")}
module_list = Path("/proc/modules").read_text(errors="replace") if Path("/proc/modules").exists() else ""
binary_paths = {name: shutil.which(name) for name in
                ("mn", "ip", "ovs-vsctl", "ovs-ofctl", "ovs-dpctl", "ovsdb-server", "ovs-vswitchd",
                 "ryu-manager", "qemu-system-x86_64", "qemu-system-aarch64", "virsh", "unshare")}
caps = status_caps()
effective = caps.get("CapEff_named", {})
run_by_name = {item["name"]: item for item in commands}
namespace_status = run_by_name.get("netns_clone", {})
ovs_status = run_by_name.get("ovs_readonly_datapaths", {})
ovs_control = run_by_name.get("ovs_readonly_status", {})
native_evidence = {
    "uid_is_root": os.geteuid() == 0,
    "cap_net_admin": effective.get("CAP_NET_ADMIN", False),
    "cap_sys_admin": effective.get("CAP_SYS_ADMIN", False),
    "netns_create_returncode": namespace_status.get("returncode"),
    "openvswitch_module_loaded": Path("/sys/module/openvswitch").exists() or "openvswitch " in module_list,
    "ovs_binaries_present": all(binary_paths.get(name) for name in ("ovs-vsctl", "ovs-dpctl", "ovs-vswitchd")),
    "ovs_datapath_read_returncode": ovs_status.get("returncode"),
    "ovs_control_read_returncode": ovs_control.get("returncode"),
    "tun_device_readable": paths["/dev/net/tun"]["readable"],
    "veth_create_test": "not_run: network interface mutation is outside preflight scope",
    "native_route_status": "not demonstrated; no topology or veth was created",
}
qemu_present = bool(binary_paths.get("qemu-system-x86_64") or binary_paths.get("qemu-system-aarch64"))
report = {
    "observed_utc": datetime.now(timezone.utc).isoformat(),
    "run_id": RUN_ID,
    "uid": os.getuid(), "euid": os.geteuid(), "capabilities": caps,
    "binary_paths": binary_paths, "device_paths": paths,
    "openvswitch_module_loaded": native_evidence["openvswitch_module_loaded"],
    "openvswitch_proc_module_excerpt": [line for line in module_list.splitlines() if line.startswith("openvswitch ")][:3],
    "commands": commands,
    "native_path_evidence": native_evidence,
    "qemu_binary_present": qemu_present,
    "qemu_vm_started": False,
    "unshare_netns_created": namespace_status.get("returncode") == 0,
    "veth_creation_attempted": False,
    "network_interfaces_changed": False,
    "package_install_attempted": False,
    "full_capture_started": False,
    "elapsed_seconds": round(time.monotonic() - probe_started, 3),
}
write_json("capability_probe.json", report)
emit("capability_probe_complete", {"report_path": str(REMOTE_ROOT / "capability_probe.json"),
                                   "native_path_evidence": native_evidence,
                                   "qemu_binary_present": qemu_present,
                                   "elapsed_seconds": report["elapsed_seconds"]})
'''

summary_code = '''# Purpose: verify representative artifact write/read and finalize the preflight run record.
import hashlib, json, time
from datetime import datetime, timezone

emit("artifact_check_started", {"output_root": str(REMOTE_ROOT)})
marker = REMOTE_ROOT / "artifact_persistence_check.txt"
marker.write_text(f"{RUN_ID}\\n", encoding="utf-8")
readback = marker.read_text(encoding="utf-8")
artifact_check = {"path": str(marker), "bytes": marker.stat().st_size,
                  "sha256": hashlib.sha256(marker.read_bytes()).hexdigest(),
                  "readback_matches": readback == f"{RUN_ID}\\n",
                  "scope": "runtime filesystem readback only; Kaggle version persistence/retrieval verified after run"}
write_json("artifact_persistence_check.json", artifact_check)
manifest.update({"status": "completed", "completed_utc": datetime.now(timezone.utc).isoformat(),
                 "elapsed_seconds": round(time.monotonic() - started_monotonic, 3),
                 "artifact_readback_passed": artifact_check["readback_matches"],
                 "files_expected": ["environment.json", "provenance.json", "capability_probe.json",
                                    "artifact_persistence_check.json", "run_manifest.json",
                                    "logs/cell_stdout.log", "logs/command_results.jsonl"]})
write_json("run_manifest.json", manifest)
print(json.dumps({"status": manifest["status"], "run_id": RUN_ID,
                  "output_root": str(REMOTE_ROOT), "elapsed_seconds": manifest["elapsed_seconds"],
                  "artifact_readback_passed": artifact_check["readback_matches"]}, indent=2), flush=True)
'''

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Kaggle CPU runtime capability preflight\n",
            "\n",
            "Purpose: check hosted runtime identity, UID/capabilities, network namespace support, existing TUN/OVS tooling and read-only datapath visibility. This run does not install packages, create veth devices, change interfaces, start services, boot QEMU, generate traffic, or capture the planned dataset.\n",
            "\n",
            f"Project: {PROJECT}. Source snapshot SHA-256: `{source_snapshot}`. Frozen design config SHA-256: `{source_hashes[SNAPSHOT_FILES[0]]}`. Intended target: Kaggle CPU. Output: `/kaggle/working/experiments/topology_dataset/runs/{RUN_ID}/`.\n",
            "\n",
            "Environment: Kaggle managed Python CPU image, executed remotely from a clean kernel version. Dependencies: Python standard library only; no local project dependency file is required for this capability probe, and no packages are installed. The preflight does not assume a full repository checkout is mounted; the setup cell reports the resolved path if one is present.\n",
        ],
    },
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": setup_code.splitlines(keepends=True)},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": capability_code.splitlines(keepends=True)},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": summary_code.splitlines(keepends=True)},
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "kaggle": {"accelerator": "none", "isGpuEnabled": False, "isInternetEnabled": False,
                   "language": "python", "sourceType": "notebook"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
notebook_path = NOTEBOOK_DIR / "01_kaggle_capture.ipynb"
notebook_path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

metadata = {
    "id": f"{OWNER}/{SLUG}",
    "title": "SDN DDoS Topology Capture",
    "code_file": notebook_path.name,
    "language": "python",
    "kernel_type": "notebook",
    "is_private": True,
    "enable_gpu": False,
    "enable_tpu": False,
    "enable_internet": False,
    "machine_shape": "",
    "dataset_sources": [],
    "competition_sources": [],
    "kernel_sources": [],
    "model_sources": [],
}
metadata_path = NOTEBOOK_DIR / "kernel-metadata.json"
metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

local_run = ROOT / "experiments/topology_dataset/runs" / RUN_ID
local_run.mkdir(parents=True, exist_ok=True)
(local_run / "local_provenance.json").write_text(
    json.dumps({
        "run_id": RUN_ID,
        "owner": OWNER,
        "notebook_slug": SLUG,
        "source_snapshot_sha256": source_snapshot,
        "source_file_sha256": source_hashes,
        "notebook_sha256": sha256_file(notebook_path),
        "metadata_sha256": sha256_file(metadata_path),
        "created_utc": created_utc,
        "local_repository_revision": "unavailable: destination is not a Git checkout",
        "commands": [
            "kaggle kernels push -p experiments/topology_dataset/notebooks -t 900",
            f"kaggle kernels status {OWNER}/{SLUG}",
            f"kaggle kernels output {OWNER}/{SLUG} -p experiments/topology_dataset/runs/{RUN_ID}/retrieved",
        ],
        "scope": "Kaggle CPU capability preflight only; no dataset generation",
    }, indent=2) + "\n",
    encoding="utf-8",
)

print(json.dumps({
    "run_id": RUN_ID,
    "notebook_path": str(notebook_path),
    "metadata_path": str(metadata_path),
    "local_run_path": str(local_run),
    "source_snapshot_sha256": source_snapshot,
    "source_file_sha256": source_hashes,
    "notebook_sha256": sha256_file(notebook_path),
}, indent=2))
