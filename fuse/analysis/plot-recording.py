#!/usr/bin/env python

import argparse
import os
import sys

import matplotlib.pylab as plt
import pandas
import seaborn as sns

here = os.path.dirname(__file__)
sys.path.insert(0, here)
from container_recorder import Filesystem, Traces


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

    plt.figure(figsize=(20, 20))
    df.index = [os.path.basename(x) for x in df.index]
    sns.clustermap(df, mask=(df == 0.0), cmap="crest")

    # Save all the things!
    plot_path = os.path.join(
        args.outdir, f"{args.name}-top-{args.n}-recorded-paths.png"
    )
    title = f"{args.name} Top (N={args.n}) Recorded Paths"
    plt.title(title.rjust(70), fontsize=10)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    # Next, let's create a plot across binaries of a Trie
    fs = Filesystem()
    for i, (path, count) in enumerate(counts.items()):
        # Only plot top N requested by user
        if i > args.n:
            break
        fs.insert(path, count=count)

    # Generate graph. This adds to matplotlib context
    fs.get_graph(title=f"Filesystem Recording Trie for {args.name} Top {args.n} Recorded Paths")
    plot_path = os.path.join(
        args.outdir, f"{args.name}-top-{args.n}-recorded-paths-trie.png"
    )
    plt.savefig(plot_path)

    # How to interact with fs
    # This path is not in the top 10, so will return None
    inode = fs.find("/opt/lammps/examples/reaxff/HNS/in.reaxff.hns")

    # This path IS in the top 10, so we get a node back
    inode = fs.find("/opt/lammps/examples/reaxff/HNS/ffield.reax.hns")
    print(f"{inode.name} is recorded {inode.count} times across recordings.")


if __name__ == "__main__":
    main()
