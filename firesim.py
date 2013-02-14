import sys
import logging as log

from firesimgui import FireSimGUI
from util.arguments import parse_args


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    log.info("Booting FireSim...")
    args = parse_args()
    sim = FireSimGUI(args)
    sys.exit(sim.run())

