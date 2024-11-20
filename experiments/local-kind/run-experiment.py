#!/usr/bin/env python3

import argparse
import json
import os
import time
import sys
from jinja2 import Template

from kubernetes import client, config

config.load_kube_config()

# import the script we have two levels up
here = os.path.abspath(os.path.dirname(__file__))


def read_file(filename):
    with open(filename, "r") as fd:
        content = fd.read()
    return content


def write_file(content, filename):
    with open(filename, "w") as fd:
        fd.write(content)


minicluster_template = read_file(os.path.join(here, "minicluster.yaml"))
template = Template(minicluster_template)

plans = [
    {"tag": "stable_29Aug2024_update1"},
    {"tag": "stable_29Aug2024"},
    {"tag": "patch_29Aug2024"},
    {"tag": "stable_2Aug2023_update4", "infile": "./in.reaxc.hns"},
    {"tag": "patch_27Jun2024"},
    {"tag": "patch_17Apr2024"},
    {"tag": "stable_2Aug2023_update3"},
    {"tag": "patch_7Feb2024_update1"},
    {"tag": "patch_7Feb2024"},
    {"tag": "stable_2Aug2023_update2", "infile": "./in.reaxc.hns"},
    {"tag": "patch_21Nov2023", "infile": "./in.reaxc.hns"},
    {"tag": "stable_2Aug2023_update1", "infile": "./in.reaxc.hns"},
    {"tag": "stable_2Aug2023", "infile": "./in.reaxc.hns"},
    {"tag": "patch_2Aug2023", "infile": "./in.reaxc.hns"},
    {"tag": "patch_15Jun2023", "infile": "./in.reaxc.hns"},
    {"tag": "stable_23Jun2022_update4", "infile": "./in.reaxc.hns"},
    {"tag": "patch_28Mar2023_update1", "infile": "./in.reaxc.hns"},
    {"tag": "patch_28Mar2023", "infile": "./in.reaxc.hns"},
    {"tag": "stable_23Jun2022_update3", "infile": "./in.reaxc.hns"},
    {"tag": "patch_8Feb2023", "infile": "./in.reaxc.hns"},
    {"tag": "patch_22Dec2022", "infile": "./in.reaxc.hns"},
    {"tag": "stable_23Jun2022_update2", "infile": "./in.reaxc.hns"},
    {"tag": "patch_3Nov2022", "infile": "./in.reaxc.hns"},
    {"tag": "patch_15Sep2022", "infile": "./in.reaxc.hns"},
    {"tag": "stable_23Jun2022_update1", "infile": "./in.reaxc.hns"},
    {"tag": "patch_3Aug2022", "infile": "./in.reaxc.hns"},
    {"tag": "stable_23Jun2022", "infile": "./in.reaxc.hns"},
    {"tag": "patch_23Jun2022", "infile": "./in.reaxc.hns"},
    {"tag": "patch_2Jun2022", "infile": "./in.reaxc.hns"},
    {"tag": "patch_4May2022", "infile": "./in.reaxc.hns"},
    {"tag": "stable_29Sep2021_update3", "infile": "./in.reaxc.hns"},
    {"tag": "patch_24Mar2022", "infile": "./in.reaxc.hns"},
    {"tag": "patch_17Feb2022", "infile": "./in.reaxc.hns"},
    {"tag": "stable_29Sep2021_update2", "infile": "./in.reaxc.hns"},
    {"tag": "patch_7Jan2022", "infile": "./in.reaxc.hns"},
    {"tag": "patch_14Dec2021", "infile": "./in.reaxc.hns"},
    {"tag": "stable_29Sep2021_update1", "infile": "./in.reaxc.hns"},
    {"tag": "patch_27Oct2021", "infile": "./in.reaxc.hns"},
    {"tag": "stable_29Sep2021", "infile": "./in.reaxc.hns"},
    {"tag": "patch_29Sep2021", "infile": "./in.reaxc.hns"},
    {"tag": "patch_20Sep2021", "infile": "./in.reaxc.hns"},
    {"tag": "patch_31Aug2021", "infile": "./in.reaxc.hns"},
    {"tag": "patch_30Jul2021", "infile": "./in.reaxc.hns"},
    {"tag": "patch_28Jul2021", "infile": "./in.reaxc.hns"},
    {
        "tag": "patch_2Jul2021",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_27May2021",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_14May2021",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_8Apr2021",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_10Mar2021",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_10Feb2021",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_24Dec2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_30Nov2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "stable_29Oct2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_29Oct2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_22Oct2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_9Oct2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_18Sep2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_24Aug2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_21Aug2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_21Jul2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_30Jun2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_15Jun2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_2Jun2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_5May2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_15Apr2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_19Mar2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "stable_3Mar2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_3Mar2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_3Mar2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_27Feb2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_18Feb2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_4Feb2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_24Jan2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_9Jan2020",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_20Nov2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_30Oct2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_19Sep2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "stable_7Aug2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_7Aug2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_6Aug2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_2Aug2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_19Jul2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_18Jun2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "stable_5Jun2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_5Jun2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
    {
        "tag": "patch_31May2019",
        "infile": "./in.reaxc.hns",
        "workdir": "/opt/lammps/examples/reax/HNS",
    },
]


def get_parser():
    parser = argparse.ArgumentParser(
        description="LAMMPS Recording Experiment Running",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--name",
        help="name for minicluster (defaults to flux-sample)",
        default="flux-sample",
    )
    parser.add_argument(
        "--data-dir",
        help="path to save data",
        default=os.path.join(here, "data", "raw"),
    )
    parser.add_argument(
        "--x",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--y",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--z",
        type=int,
        default=4,
    )
    return parser


def read_json(filename):
    """
    Read json from file.
    """
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def confirm_action(question):
    """
    Ask for confirmation of an action
    """
    response = input(question + " (yes/no)? ")
    while len(response) < 1 or response[0].lower().strip() not in "ynyesno":
        response = input("Please answer yes or no: ")
    if response[0].lower().strip() in "no":
        return False
    return True


def generate_uid(params):
    """
    Generate a unique id based on params.
    """
    uid = ""
    for k, v in params.items():
        if not isinstance(v, dict):
            uid += k.lower() + "-" + str(v).lower()
        else:
            uid += k.lower()
    return uid


def write_json(obj, filename):
    """
    write json to output file
    """
    with open(filename, "w") as fd:
        fd.write(json.dumps(obj, indent=4))


def run_lammps(exp, args, data_path):
    """
    Run LAMMPS for some number of iterations
    """
    tag = exp["tag"]
    tag_dir = os.path.join(data_path, tag)
    outfile = os.path.join(tag_dir, "lammps-recording.out")
    if os.path.exists(outfile):
        print(f"{outfile} exists, skipping")
        return
    print(f"\n🪔️ Running LAMMPS release {tag}")
    exp.update({"name": args.name, "x": args.x, "y": args.y, "z": args.z})
    render = template.render(**exp)
    lammps_yaml = os.path.join(tag_dir, "minicluster.yaml")
    write_file(render, lammps_yaml)
    run_kubectl(f"apply -f {lammps_yaml}")
    time.sleep(10)

    # This will wait for it to finish
    run_kubectl("wait --for=condition=complete --timeout=600s job/flux-sample")

    cli = client.CoreV1Api()
    for pod in cli.list_namespaced_pod(namespace="default").items:
        if f"{args.name}-0" in pod.metadata.name:
            log = cli.read_namespaced_pod_log(
                name=pod.metadata.name, namespace="default"
            )
            break

    # Save to file
    print(f"Writing lammps log and recordings to {outfile}")
    write_file(log, outfile)

    # Wait for all pods to terminate
    run_kubectl(f"delete -f {lammps_yaml} --wait=true", allow_fail=True)


def run_kubectl(command, allow_fail=False):
    """
    Wrapper to client to run command with kubeconfig file
    """
    command = f"kubectl {command}"
    res = os.system(command)
    if res != 0 and not allow_fail:
        print(
            f"ERROR: running {command} - debug and ensure it works before exiting from session."
        )
        import IPython

        IPython.embed()
    return res


def run_experiments(args):
    """
    Generate runs for miniclusters to run lammps
    """
    # Note that the experiment already has a table of values filtered down
    # Each experiment has some number of batches (we will typically just run one experiment)
    total = len(plans)
    for i, exp in enumerate(plans):
        print(f"== Running experiment {exp}: {i} of {total}")

        # Save the entire table just once
        path = os.path.join(args.data_dir, exp["tag"])
        if not os.path.exists(path):
            os.makedirs(path)

        # EXPERIMENTS: ---
        # Run LAMMPS a number of iterations in the cluster
        # This writes all iteration runs to one output file
        try:
            run_lammps(exp, args, args.data_dir)
            tag = exp["tag"]

            # Clean up as we go
            os.system(f"docker rmi ghcr.io/converged-computing/lammps-time-fuse:{tag}")
        except:
            print(f"Issue with {exp} - investigate!")

    print("Experiments are done!")


def main():
    """
    Run experiments for lammps, and collect hwloc info.
    """
    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, _ = parser.parse_known_args()
    if not os.path.exists(args.data_dir):
        os.makedirs(args.data_dir)

    # plan experiments!
    print("🧪️ Experiments:")
    for plan in plans:
        print(f"   {plan['tag']}")

    print("🪴️ Planning to run:")
    print(f"   Output Data         : {args.data_dir}")
    print(f"   Experiments         : {len(plans)}")
    if not confirm_action("Would you like to continue?"):
        sys.exit("📺️ Cancelled!")

    # Main experiment running, show total time just for user FYI
    start_experiments = time.time()
    run_experiments(args)
    stop_experiments = time.time()
    total = stop_experiments - start_experiments
    print(f"total time to run is {total} seconds")


if __name__ == "__main__":
    main()
