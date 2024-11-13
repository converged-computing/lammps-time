#!/usr/bin/env python

import argparse
import os
import sys
import seaborn as sns
import matplotlib.pylab as plt

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
    parser.add_argument(
        "--outdir",
        help="Output directory for images",
        default=os.path.join(here, "img"),
    )
    parser.add_argument("--name", help="Application name", default="LAMMPS")
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

    # Clean up release names
    sims.index = [x.replace(".out", "").replace("lammps-", "") for x in sims.index]
    sims.columns = [x.replace(".out", "").replace("lammps-", "") for x in sims.columns]
    plt.figure(figsize=(20, 20))
    sns.clustermap(sims.astype(float), mask=(sims == 0.0), cmap="tab20b")

    # Save all the things!
    plot_path = os.path.join(args.outdir, f"{args.name}-levenstein-distance-matrix.png")
    title = f"Levenstein Distance of File Access for 86 Recorded {args.name} Release Runs (2019-2024)"
    plt.title(title.rjust(200), fontsize=10)
    plt.tight_layout()
    plt.xlabel("Release Tag")
    plt.ylabel("Release Tag")
    plt.savefig(plot_path)
    plt.close()


if __name__ == "__main__":
    main()
