"""Incremental cell capture after package bootstrap; preserves displayed rich outputs."""
import sys
import time
import traceback
from pathlib import Path
import nbformat
from sdn_ddos.runtime.run import Tee, write_json


def install_capture(directory):
    from IPython import get_ipython
    shell = get_ipython()
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    notebook = nbformat.v4.new_notebook()
    state = {}
    publisher = shell.display_pub.publish

    def publish(data, metadata=None, **kwargs):
        if state.get('cell') is not None:
            state['cell'].outputs.append(nbformat.v4.new_output('display_data', data=data, metadata=metadata or {}))
        return publisher(data=data, metadata=metadata, **kwargs)

    def before(info):
        index = len(notebook.cells)
        cell = nbformat.v4.new_code_cell(info.raw_cell, execution_count=shell.execution_count)
        notebook.cells.append(cell)
        log = (directory / f'cell-{index:03d}.log').open('w', encoding='utf-8')
        state.update(cell=cell, log=log, stdout=sys.stdout, stderr=sys.stderr, started=time.monotonic())
        sys.stdout, sys.stderr = Tee(sys.stdout, log), Tee(sys.stderr, log)
        print('CELL START', index, flush=True)
        nbformat.write(notebook, directory / 'executed_cells.ipynb')

    def after(result):
        if not state:
            return
        error = result.error_before_exec or result.error_in_exec
        cell = state['cell']
        cell.metadata['status'] = 'failed' if error else 'complete'
        cell.metadata['seconds'] = time.monotonic() - state['started']
        if error:
            cell.outputs.append(nbformat.v4.new_output('error', ename=type(error).__name__, evalue=str(error),
                                                       traceback=traceback.format_exception(type(error), error, error.__traceback__)))
        print('CELL END', len(notebook.cells) - 1, cell.metadata, flush=True)
        sys.stdout, sys.stderr = state['stdout'], state['stderr']
        state['log'].close()
        logpath = directory / f'cell-{len(notebook.cells)-1:03d}.log'
        cell.outputs.insert(0, nbformat.v4.new_output('stream', name='stdout', text=logpath.read_text(encoding='utf-8')))
        nbformat.write(notebook, directory / 'executed_cells.ipynb')
        write_json(directory / 'cell_ledger.json', [dict(index=i, **c.metadata) for i, c in enumerate(notebook.cells)])
        state.clear()

    shell.display_pub.publish = publish
    shell.events.register('pre_run_cell', before)
    shell.events.register('post_run_cell', after)
    print('Cell capture enabled:', directory, '; bootstrap-cell output remains in the native Kaggle log', flush=True)

