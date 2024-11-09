#!/usr/bin/env python

import argparse
import sys
import os

here = os.path.dirname(__file__)
sys.path.insert(0, here)
from container_recorder import Traces


def get_parser():
    parser = argparse.ArgumentParser(
        description="Analyze Two Recordings from fs-record",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-o",
        "--outfile",
        help="Output file for results",
    )
    return parser


def main():
    p = get_parser()

    # Extra events here should be one or more result event files to parse
    args, events = p.parse_known_args()
    simcalc = Traces(events)
    df = simcalc.to_dataframe()
    df.to_csv("testing-lammps-same.csv")
    sims = simcalc.distance_matrix()
    print(sims)


if __name__ == "__main__":
    main()
