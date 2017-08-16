import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="FireSim")
    parser.add_argument("--profile", action='store_const', const=True, default=False, help="Enable profiling")
    parser.add_argument('--scene', type=str, help="Scene to load")
    return parser.parse_args()
