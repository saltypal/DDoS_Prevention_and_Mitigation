"""Launch the pinned Ryu stack with its existing Eventlet compatibility shim."""
import eventlet.wsgi

if not hasattr(eventlet.wsgi, 'ALREADY_HANDLED'):
    eventlet.wsgi.ALREADY_HANDLED = object()

from ryu.cmd.manager import main

if __name__ == '__main__':
    main()
