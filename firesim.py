import sys
import logging as log

from firesimgui import FireSimGUI


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    log.info("Booting FireSim...")
    sim = FireSimGUI()
    sys.exit(sim.run())

