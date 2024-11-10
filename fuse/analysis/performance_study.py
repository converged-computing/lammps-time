#!/usr/bin/env python3

# Shared functions to use across analyses.

import json
import os
import re

from matplotlib.ticker import FormatStrFormatter
import matplotlib.pylab as plt
import pandas
import seaborn as sns

sns.set_theme(style="whitegrid", palette="pastel")


def read_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def recursive_find(base, pattern="*.*"):
    """
    Recursively find and yield directories matching a glob pattern.
    """
    for root, dirnames, filenames in os.walk(base):
        for dirname in dirnames:
            if not re.search(pattern, dirname):
                continue
            yield os.path.join(root, dirname)


def recursive_find_files(base, pattern="*.*"):
    """
    Recursively find and yield directories matching a glob pattern.
    """
    for root, _, filenames in os.walk(base):
        for filename in filenames:
            if not re.search(pattern, filename):
                continue
            yield os.path.join(root, filename)


def find_inputs(input_dir, pattern="*.*"):
    """
    Find inputs (times results files)
    """
    files = []
    for filename in recursive_find(input_dir, pattern):
        # We only have data for small
        files.append(filename)
    return files


def read_file(filename):
    with open(filename, "r") as fd:
        content = fd.read()
    return content


def write_json(obj, filename):
    with open(filename, "w") as fd:
        fd.write(json.dumps(obj, indent=4))


def write_file(text, filename):
    with open(filename, "w") as fd:
        fd.write(text)


class ExperimentNameParser:
    """
    Shared parser to convert directory path into components.
    """

    def __init__(self, filename, indir):
        self.filename = filename
        self.indir = indir
        self.parse()

    def parse(self):
        basename = os.path.basename(self.filename)
        self.tag = basename.replace(".out", "").replace("lammps-", "")


class ResultParser:
    """
    Extended ResultParser that includes a problem size.
    """

    def __init__(self, app):
        self.init_df()
        self.idx = 0
        self.app = app

    def set_context(self, tag):
        self.tag = tag
        # Janky way to parse the year
        match = re.search("(2018|2019|2020|2021|2022|2023|2024)", tag)
        self.year = match.group()

    def init_df(self):
        """
        Initialize an empty data frame for the application
        """
        self.df = pandas.DataFrame(
            columns=[
                "tag",
                "year",
                "nodes",
                "application",
                "problem_size",
                "metric",
                "value",
            ]
        )

    def add_result(self, metric, value, problem_size):
        """
        Add a result to the table
        """
        # Unique identifier for the experiment plot
        # is everything except for size
        self.df.loc[self.idx, :] = [
            self.tag,
            self.year,
            1,  # 1 node, my computer :)
            self.app,
            problem_size,
            metric,
            value,
        ]
        self.idx += 1


def make_plot(
    df,
    title,
    ydimension,
    xdimension,
    xlabel,
    ylabel,
    palette=None,
    ext="png",
    plotname="lammps",
    hue=None,
    outdir="img",
    log_scale=False,
    do_round=False,
):
    """
    Helper function to make common plots.
    """
    ext = ext.strip(".")
    plt.figure(figsize=(12, 6))
    sns.set_style("dark")
    flierprops = dict(
        marker=".", markerfacecolor="None", markersize=10, markeredgecolor="black"
    )
    ax = sns.boxplot(
        x=xdimension,
        y=ydimension,
        flierprops=flierprops,
        hue=hue,
        data=df,
        # gap=.1,
        linewidth=0.4,
        palette=palette,
        whis=[5, 95],
        # dodge=False,
    )

    plt.title(title)
    print(log_scale)
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize=14)
    ax.set_yticklabels(ax.get_yticks(), fontsize=14)
    # plt.xticks(rotation=90)
    if log_scale is True:
        plt.gca().yaxis.set_major_formatter(
            plt.ScalarFormatter(useOffset=True, useMathText=True)
        )

    if do_round is True:
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"{plotname}.{ext}"))
    plt.clf()
