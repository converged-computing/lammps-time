#!/usr/bin/env python3

import argparse
import collections
import os
import sys

from metricsoperator.metrics.app.lammps import parse_lammps
import matplotlib.pylab as plt
import seaborn as sns

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
sys.path.insert(0, here)

import performance_study as ps

sns.set_theme(style="whitegrid", palette="pastel")


def get_parser():
    parser = argparse.ArgumentParser(
        description="Run output analysis",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--root",
        help="root directory with experiments",
        default=os.path.join(root, "output"),
    )
    parser.add_argument(
        "--out",
        help="directory to save parsed results",
        default=os.path.join(here, "data"),
    )
    return parser


def main():
    """
    Find application result files to parse.
    """
    parser = get_parser()
    args, _ = parser.parse_known_args()

    # Output images and data
    outdir = os.path.abspath(args.out)
    indir = os.path.abspath(args.root)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Find input directories (anything with lammps-reax)
    # lammps directories are usually snap
    files = ps.recursive_find_files(indir, "lammps-")
    if not files:
        raise ValueError(f"There are no input files in {indir}")

    # Saves raw data to file
    df = parse_data(indir, outdir, files)
    plot_results(df, outdir)


def parse_data(indir, outdir, files):
    """
    Parse filepaths for environment, etc., and results files for data.
    """
    # metrics here will be wall time and wrapped time
    p = ps.ResultParser("lammps")

    # For flux we can save jobspecs and other event data
    data = {}

    # It's important to just parse raw data once, and then use intermediate
    for filename in files:
        exp = ps.ExperimentNameParser(filename, indir)

        # Set the parsing context for the result data frame
        item = ps.read_file(filename)
        p.set_context(exp.tag)

        # Problem size is just 2x2x2
        problem_size = "2x2x2"
        lammps_result = parse_lammps(item)
        if not lammps_result:
            print(f"Warning: no result for {filename}")
            continue

        # Add in Matom steps - what is considered the LAMMPS FOM
        # https://asc.llnl.gov/sites/asc/files/2020-09/CORAL2_Benchmark_Summary_LAMMPS.pdf
        # Not parsed by metrics operator so we find the line here
        if "Matom" in item:
            line = [x for x in item.split("\n") if "Matom-step/s" in x][0]
            matom_steps_per_second = float(line.split(",")[-1].strip().split(" ")[0])
            p.add_result("matom_steps_per_second", matom_steps_per_second, problem_size)

        wall_time = lammps_result["total_wall_time_seconds"]
        p.add_result("wall_time", wall_time, problem_size)
        p.add_result("ranks", lammps_result["ranks"], problem_size)

        # CPU utilization
        line = [x for x in item.split("\n") if "CPU use" in x][0]
        cpu_util = float(line.split(" ")[0].replace("%", ""))
        p.add_result("cpu_utilization", cpu_util, problem_size)
        lammps_result["cpu_utilization"] = cpu_util
        data[exp.tag] = lammps_result

    print("Done parsing lammps results!")
    p.df.to_csv(os.path.join(outdir, "lammps-reax-results.csv"))
    ps.write_json(data, os.path.join(outdir, "lammps-reax-parsed.json"))
    return p.df


def plot_results(df, outdir):
    """
    Plot analysis results
    """
    # Let's get some shoes! Err, plots.
    # Make an image outdir
    img_outdir = os.path.join(outdir, "img")
    if not os.path.exists(img_outdir):
        os.makedirs(img_outdir)

    # We only have the variable of tags by metric / values
    for metric in df.metric.unique():
        if metric == "ranks":
            continue
        metric_df = df[df.metric == metric]
        colors = sns.color_palette("hls", len(metric_df.year.unique()))
        hexcolors = colors.as_hex()
        types = list(metric_df.year.unique())
        types.sort()
        palette = collections.OrderedDict()
        for t in types:
            palette[t] = hexcolors.pop(0)
        title = " ".join([x.capitalize() for x in metric.split("_")])
        number_years = len(types)
        problem_size = "2x2x2"
        metric_df = metric_df.sort_values("year")
        ps.make_plot(
            metric_df,
            title=f"LAMMPS Metric {title} {problem_size} Releases Over {number_years} Years",
            ydimension="value",
            plotname=f"lammps-reax-{metric}-{problem_size}-{number_years}",
            xdimension="year",
            palette=palette,
            outdir=img_outdir,
            hue="year",
            xlabel="Year",
            ylabel=title,
            do_round=True,
        )

    # Just do a line plot of releases over time
    metric_df = metric_df.sort_values(["year", "tag"])
    ax = sns.scatterplot(
        x="tag",
        y="value",
        hue="year",
        data=metric_df,
        palette=palette,
    )
    title = f"LAMMPS Metric {metric} ({problem_size}) Releases Over {number_years} Years"
    plt.title(title)
    ax.set_xlabel("Release Tag", fontsize=12)
    ax.set_ylabel(metric.split("_"), fontsize=12)
    ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize=12)
    ax.set_yticklabels(ax.get_yticks(), fontsize=12)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(
        os.path.join(
            img_outdir,
            f"lammps-reax-{metric}-{problem_size}-{number_years}-by-release.png",
        )
    )
    plt.clf()


if __name__ == "__main__":
    main()
