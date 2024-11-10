#!/usr/bin/env python

import pandas
import argparse
import matplotlib.pylab as plt
import seaborn as sns
import sys
import os

here = os.path.dirname(__file__)
sys.path.insert(0, here)
from container_recorder import Traces


def get_parser():
    parser = argparse.ArgumentParser(
        description="Plot Recordings from fs-record",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-o",
        "--outdir",
        help="Output directory for images",
        default=os.path.join(here, "img"),
    )
    parser.add_argument("--name", help="Application name", default="LAMMPS")
    parser.add_argument(
        "-n",
        help="Plot the top N paths",
        type=int,
        default=20,
    )
    return parser


def main():
    p = get_parser()

    # Extra events here should be one or more result event files to parse
    args, events = p.parse_known_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    simcalc = Traces(events)

    # Get all counts so we can get the top 10 across them
    counts = simcalc.all_counts()
    if len(counts) < args.n:
        args.n = len(counts) - 1
    shared_paths = list(counts)[: args.n]

    # We will make a nice heatmap of files by recorded opens
    df = pandas.DataFrame(0, columns=shared_paths, index=simcalc.files)

    for path, trace in simcalc.as_counts(fullpath=True).items():
        single_trace = {p: 0 for p in shared_paths}
        for k, v in trace.items():
            # Don't add any not in the shared set
            if k not in single_trace:
                continue
            single_trace[k] = v
        df.loc[path] = single_trace

    plt.figure(figsize=(20, 18))
    sns.heatmap(df, mask=(df == 0.0), cmap="crest", annot=df)

    # Save all the things!
    plot_path = os.path.join(
        args.outdir, f"{args.name}-top-{args.n}-recorded-paths.png"
    )
    plt.title(f"{args.name} Top (N={args.n}) Recorded Paths", fontsize=16)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()


if __name__ == "__main__":
    main()
