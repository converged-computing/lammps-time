ARG tag
FROM ghcr.io/converged-computing/lammps-time:${tag}
# We need fuse in the container
# docker build -f Dockerfile.lammps -t ghcr.io/converged-computing/lammps-time:stable_29Aug2024_update1-fuse .
RUN apt-get update && apt-get install -y fuse libfuse-dev proot && apt-get clean
