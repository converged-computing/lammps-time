#!/usr/bin/env python

import argparse
import os
import sys
import pandas
import matplotlib.pylab as plt
from scipy.stats import poisson
from numpy.random import choice
import numpy

from matplotlib.backends.backend_pdf import PdfPages

from itertools import cycle

here = os.path.dirname(__file__)
sys.path.insert(0, here)
from container_recorder import Traces


def get_parser():
    parser = argparse.ArgumentParser(
        description="Build models for fs recordings",
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

    # Test 1: Simple Markov Model.
    # Let's generate a transition matrix based on unique paths
    # Let's do leave one out cross validation to use each as a test sample
    # And then just predict each path based on the previous and calculate
    # a total accuracy (correct / total) for the entire set.
    results = {"correct": 0, "wrong": 0}
    for train, test, _ in simcalc.iter_loo():
        for key, value in build_and_test_markov(train, test).items():
            if key.startswith("transition"):
                continue
            results[key] += value

    print("Markov Model Results")
    print_results(results)

    # Let's compare to overall frequency - so ONE row that we do counts, and then
    # run the same procedure for. We could call this a 0-gram model :)
    frequency_results = build_and_test_frequency_model(simcalc.samples)
    print("Frequency Results")
    print_results(frequency_results)

    # Test 2: Hidden Markov Models with Conditional Transition Times
    # We start with our same matrix of transition probabilities, but we also construct
    # a matrix of mean timeseries (Poisson distributed)
    # The results are residuals, so we can look at the error
    residuals = {}
    for train, test, left_out in simcalc.iter_loo():
        # This takes the time in the state into account
        for path, new_residuals in build_and_test_markov_with_times(
            df, train, test, left_out
        ).items():
            if path not in residuals:
                residuals[path] = []
            residuals[path] += new_residuals

    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True

    # Make different colors!
    colors = cycle("bgrcmk")

    # Plot a histogram for each
    for path, residual_set in residuals.items():
        # This is important so each is a new figure
        plt.figure()
        plt.hist(residual_set, color=next(colors))
        plt.title(path)
    save_histogram_pdf(os.path.join(args.outdir, "residuals-for-paths-normalized.pdf"))
    plt.close()
    plt.clf()


def print_results(results):
    accuracy = results["correct"] / (results["correct"] + results["wrong"])
    print(f"  Leave one out correct: {results['correct']}")
    print(f"    Leave one out wrong: {results['wrong']}")
    print(f"          correct/total: {accuracy}")


def save_histogram_pdf(save_path):
    """
    Save current plotting context to pdf with PdfPages.
    """
    # Get handles for all figures in plotting context
    fig_nums = plt.get_fignums()
    figs = [plt.figure(n) for n in fig_nums]

    # iterating over the numbers in list
    with PdfPages(save_path) as p:
        for fig in figs:
            fig.savefig(p, format="pdf")


def build_and_test_frequency_model(samples):
    """
    I don't know if there is a name for this, but a "base case" to test
    against the Markov model would be to use the frequencies across
    all datasets -> paths for the path instead one one scoped to the
    previous path.
    """
    unique_paths = list(set([x for xs in samples for x in xs]))
    tm = pandas.DataFrame(0, index=unique_paths, columns=["frequency"])
    for paths in samples:
        for path in paths:
            tm.loc[path, "frequency"] += 1

    # Make sure each row sums to 1
    tm_norm = tm.div(tm.sum(axis=0), axis=1)
    results = {"correct": 0, "wrong": 0}

    # This is the list of paths we can choose from for the next
    path_selection = tm_norm.index.tolist()
    probabilities = tm_norm["frequency"].values.tolist()
    for test in samples:
        for i, path in enumerate(test):
            if i + 1 >= len(test):
                break
            # Make a choice and see if it's right.
            draw = choice(path_selection, 1, p=probabilities)
            if draw[0] == path:
                results["correct"] += 1
            else:
                results["wrong"] += 1
    return results


def test_markov(tm_norm, test):
    """
    Given a test vector, test against a normalized transition matrix.
    """
    # Keep track of correct, wrong, and the transitions
    results = {
        "correct": 0,
        "wrong": 0,
        "transitions-correct": [],
        "transitions-incorrect": [],
    }

    # Let's use leave one out cross validation to test our model
    for i, path in enumerate(test):
        if i + 1 >= len(test):
            break
        # This is the path we are trying to predict
        next_path = test[i + 1]

        # This is the list of paths we can choose from for the next
        path_selection = tm_norm.loc[path].index.tolist()

        # These are the probabilities of each
        probabilities = tm_norm.loc[path].values.tolist()

        # Make a choice and see if it's right.
        draw = choice(path_selection, 1, p=probabilities)
        if draw[0] == next_path:
            results["correct"] += 1
            results["transitions-correct"].append([path, draw[0]])
        else:
            results["wrong"] += 1
            results["transitions-incorrect"].append([path, draw[0]])
    return results


def build_and_test_markov(train, test):
    """
    Use leave one out strategy to get number of correct and incorrect
    predictions.
    """
    tm = build_transition_matrix(train)
    return test_markov(tm, test)


def build_and_test_markov_with_times(df, train, test, left_out):
    """
    A markov model that also accounts for the timestamps, with
    conditional transition times.
    """
    tm = build_transition_matrix(train)
    ts = build_timeseries_matrix(df, train)

    # Now we know what we transitioned to (some state, a path)
    # and we want to know the entry from the timeseries matrix, the
    # average time to go from A to T. We can use Poisson
    # (captured by mean) for the model to sample from.
    results = test_markov(tm, test)

    # Create a data frame of just left out values
    test_df = df[df.basename == left_out]

    # To calculate residuals, we are only going to consider the correct
    # transitions. I don't know how to handle transitions to the self
    # (it isn't really a change of state) so I'm going to skip.
    residuals = {}
    for result in results["transitions-correct"]:
        from_state, to_state = result
        # if the states are the same path, there is no change of state
        if from_state == to_state:
            continue
        mean_transition = ts.loc[from_state, to_state]
        dist = poisson(mean_transition)
        # Generate a random number from distribution to predict time
        predicted_time = dist.rvs(size=1)[0]
        subset = test_df[test_df.normalized_path == to_state]
        subset = subset[subset.previous_path == from_state]
        actual_time = subset.ms_in_state.values[0]

        # End of series
        if actual_time is not None:
            # Not sure if this is OK, but do the difference over the actual
            # The idea is to try and normalize the residual
            percent_diff = abs(predicted_time - actual_time) / actual_time
            if from_state not in residuals:
                residuals[from_state] = []
            residuals[from_state].append(percent_diff)
    return residuals


def build_timeseries_matrix(df, train):
    """
    The timeseries matrix calculates the mean time in a specific state,
    meaning if we move from path1 to path2 (the state being in path1)
    we record a time for all these ranges, and then put the mean in a matrix
    """
    unique_paths = list(set([x for xs in train for x in xs]))

    # Calculate mean of when path A goes to path B
    # Double check numerics that setting 0 is OK - the corresponding probabilty
    # of the state should be 0
    time_in_states = {}

    for paths in train:
        last_path = None
        # We can optimize here by just filling half (the diagonal)
        for path in paths:
            if last_path is None:
                last_path = path
                continue

            # Get the mean across samples (always over 100 it seems, e.g., 115)
            if last_path not in time_in_states:
                time_in_states[last_path] = {}
            # If we've already calculated for the combination, don't do it again
            if path in time_in_states[last_path]:
                continue
            subset = df[df.normalized_path == path]
            subset[subset.previous_path == last_path]
            subset[subset.previous_path == last_path].ms_in_state
            values = subset[subset.previous_path == last_path].ms_in_state
            # I visualized this - most looks Poisson
            mean_time = values.mean()
            if numpy.isnan(mean_time):
                mean_time = 0
            time_in_states[last_path][path] = mean_time
            last_path = path

    ts_df = pandas.DataFrame(0, index=unique_paths, columns=unique_paths)
    for path1, items in time_in_states.items():
        for path2, time_in_state in items.items():
            ts_df.loc[path1, path2] = time_in_state
    return ts_df


def build_transition_matrix(train):
    """
    Given paths for some training data, build a transition matrix
    """
    unique_paths = list(set([x for xs in train for x in xs]))
    tm = pandas.DataFrame(0, columns=unique_paths, index=unique_paths)

    # Now we iterate through the data and fill the matrix.
    # First it's just a count, we will normalize so sum of row is 1
    for paths in train:
        last_path = None
        # We can optimize here by just filling half (the diagonal)
        for path in paths:
            if last_path is None:
                last_path = path
                continue
            tm.loc[last_path, path] += 1
            last_path = path

    # Make sure each row sums to 1
    tm_norm = tm.div(tm.sum(axis=1), axis=0)
    return tm_norm


if __name__ == "__main__":
    main()
