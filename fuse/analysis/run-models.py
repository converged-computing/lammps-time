#!/usr/bin/env python

import argparse
import os
import sys
import pandas
import seaborn as sns
import matplotlib.pylab as plt
from numpy.random import choice

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
    paths = df.normalized_path.unique().tolist()

    # Let's do leave one out cross validation to use each as a test sample
    # And then just predict each path based on the previous and calculate
    # a total accuracy (correct / total) for the entire set.
    samples = list(simcalc.as_paths().values())
    results = {"correct": 0, "wrong": 0}
    total = len(samples)
    for s in range(len(samples)):
        print(f"Leaving out {s} of {total}")
        train = [x for i, x in enumerate(samples) if i != s]
        test = samples[s]
        for key, value in build_and_test_markov(train, test).items():
            results[key] += value

    print("Markov Model Results")
    print_results(results)

    # Let's compare to overall frequency - so ONE row that we do counts, and then
    # run the same procedure for. We could call this a 0-gram model :)
    frequency_results = build_and_test_frequency_model(samples)
    print("Frequency Results")
    print_results(frequency_results)


def print_results(results):
    accuracy = results["correct"] / (results["correct"] + results["wrong"])
    print(f"  Leave one out correct: {results['correct']}")
    print(f"    Leave one out wrong: {results['wrong']}")
    print(f"          correct/total: {accuracy}")


def build_and_test_frequency_model(samples):
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
    results = {"correct": 0, "wrong": 0}

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
        else:
            results["wrong"] += 1
    return results


def build_and_test_markov(train, test):
    """
    Use leave one out strategy to get number of correct and incorrect
    predictions.
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
    return test_markov(tm_norm, test)


if __name__ == "__main__":
    main()
