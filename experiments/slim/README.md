# Slim

This is a quick analysis to see if using our recording tool to capture the open paths (and save them) and then add them on top of an ubuntu:22.04 base can slim our containers (and the containers still work). The container was generated as follows [here](https://github.com/compspec/compat-lib/tree/main/example/slim) and then tagged  and pushed to `ghcr.io/converged-computing/lammps-time-slim:latest` and compared to a container build that is the same (but includes everything).

## Results

```console
full_uri
ghcr.io/converged-computing/lammps-time-slim:latest                 146673741
ghcr.io/converged-computing/lammps-time:stable_29Aug2024_update1    859635692
Name: layer_size, dtype: object
```
