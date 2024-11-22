import argparse
import compatlib.utils as utils
import os

here = os.path.dirname(os.path.abspath(__file__))


def get_parser():
    parser = argparse.ArgumentParser(
        description="Analyze Kind LAMMPS Recordings",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--indir",
        help="Input data directory",
        default=os.path.join(here, "data", "raw"),
    )
    parser.add_argument(
        "--outdir",
        help="Output directory for results",
        default=os.path.join(here, "results"),
    )
    return parser


def main():
    p = get_parser()

    # Extra events here should be one or more result event files to parse
    args, events = p.parse_known_args()

    # Let's put all recordings here
    recording_dir = os.path.join(args.outdir, "recordings")
    output_dir = os.path.join(args.outdir, "output")
    for dirname in recording_dir, output_dir:
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    # We are going to read in each output file, and generate a result
    # of recordings and LAMMPS output file
    files = utils.recursive_find_files(args.indir, "[.]out")
    for filename in files:
        # Derive the tag (release) from the directory name
        tag = os.path.basename(os.path.dirname(filename))
        content = utils.read_file(filename)

        # Split the lammps log from the recording
        lines = content.split("\n")
        idx = [i for i, x in enumerate(lines) if "START LOG" in x]
        record_idx = [i for i, x in enumerate(lines) if "START RECORDING" in x]
        if not idx or not record_idx:
            print(
                f"Warning: {filename} is missing log or recording content, must be erroneous!"
            )
            print(content)
            continue
        idx = idx[0]
        record_idx = record_idx[0]
        lammps_log = "\n".join(lines[idx + 1 : record_idx]).strip()
        lammps_recording = "\n".join(lines[record_idx + 1 :]).strip()

        # Write to file for later parsing
        log_file = os.path.join(output_dir, f"lammps-{tag}.out")
        utils.write_file(lammps_log, log_file)
        recording_file = os.path.join(recording_dir, f"lammps-{tag}.out")
        utils.write_file(lammps_recording, recording_file)


if __name__ == "__main__":
    main()
