"""Bounded live T1 forwarding pilot; saves evidence and cleans up its own nodes."""
import json
import os
from pathlib import Path
import socket
import subprocess
import time
from datetime import datetime, timezone

from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from sdn_ddos.topology import build_topology


def main():
    if os.geteuid() != 0:
        raise RuntimeError('This bounded Mininet pilot needs Linux root.')
    bridges = subprocess.check_output(['ovs-vsctl', 'list-br'], text=True).split()
    if bridges:
        raise RuntimeError(f'Existing OVS bridges require inspection before this pilot: {bridges}')
    run_id = datetime.now(timezone.utc).strftime('wsl-connectivity-%Y%m%dT%H%M%SZ')
    out = Path(__file__).resolve().parent / 'runs' / run_id
    out.mkdir(parents=True, exist_ok=False)
    report = {'run_id': run_id, 'scope': 'T1 ICMP forwarding only', 'status': 'started'}
    net = None
    controller = None
    print(f'Pilot started; evidence: {out}', flush=True)
    try:
        with (out/'controller.log').open('w') as log:
            controller = subprocess.Popen([
                '/opt/sdn-ddos-ryu-venv/bin/python', '-m', 'sdn_ddos.controller_launcher',
                '--ofp-tcp-listen-port', '16653', 'ryu.app.simple_switch_13'], stdout=log, stderr=subprocess.STDOUT)
            deadline = time.monotonic()+20
            while True:
                if controller.poll() is not None:
                    raise RuntimeError('Ryu exited; inspect controller.log')
                with socket.socket() as connection:
                    if connection.connect_ex(('127.0.0.1',16653)) == 0:
                        break
                if time.monotonic() > deadline:
                    raise TimeoutError('Ryu listener startup timed out')
                time.sleep(.2)
            net = Mininet(topo=build_topology('T1'), controller=None, switch=OVSSwitch,
                          link=TCLink, autoSetMacs=True)
            net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=16653)
            net.start()
            time.sleep(3)
            pairs = [('h11','h31'),('h21','h41'),('h12','h32')]
            report['probes'] = []
            for source, destination in pairs:
                target = net.get(destination)
                output = net.get(source).cmd(f'ping -n -c 3 -W 2 {target.IP()}')
                passed = '0% packet loss' in output and '100% packet loss' not in output
                report['probes'].append(dict(source=source,destination=destination,passed=passed,output=output))
                print(f'{source} -> {destination}: {passed}', flush=True)
            for switch in net.switches:
                dump = subprocess.check_output(['ovs-ofctl','-O','OpenFlow13','dump-flows',switch.name],text=True)
                (out/f'{switch.name}-flows.txt').write_text(dump)
            report['status'] = 'passed' if all(p['passed'] for p in report['probes']) else 'failed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = repr(error)
        raise
    finally:
        if net is not None:
            net.stop()
        if controller is not None and controller.poll() is None:
            controller.terminate()
            try:
                controller.wait(timeout=5)
            except subprocess.TimeoutExpired:
                controller.kill()
                controller.wait()
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
        (out/'report.json').write_text(json.dumps(report,indent=2))
        print(f"Pilot {report['status']}; report: {out/'report.json'}",flush=True)
    if report['status'] != 'passed':
        raise RuntimeError('Connectivity probes failed')


if __name__ == '__main__':
    main()
