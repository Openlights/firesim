import functools
import signal
import sys
import logging as log

from firesimgui import FireSimGUI
from util.arguments import parse_args

def sig_handler(app, sig, frame):
    log.info("Firesim received signal %d.  Shutting down.", sig)
    try:
        app.quit()
    except Exception:
        log.exception("Ignoring exception during shutdown request")

def main():
    log.basicConfig(level=log.WARN)
    log.info("Booting FireSim...")
    args = parse_args()
    sim = FireSimGUI(args)
    signal.signal(signal.SIGINT, functools.partial(sig_handler, sim))
    sys.exit(sim.run())

if __name__ == "__main__":
    main()
