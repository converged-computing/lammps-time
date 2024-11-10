# LAMMPS Recording

We are going to build every tag of lammps that we built in the directory above... and add fuse and proot!
Then we can run a recording session using my [fuse filesystem application recorder](https://github.com/compspec/compat-lib/?tab=readme-ov-file#3-application-recorder).

## Building Containers

First, let's build the containers (adding fuse to keep the repos separate)!

```bash
for tag in $(oras repo tags ghcr.io/converged-computing/lammps-time)
  do
    echo "Building $tag"
    docker build --build-arg tag=${tag} -t ghcr.io/converged-computing/lammps-time-fuse:${tag} .
    if [[ "${retval}" != "0" ]]; then
        echo "Tag ${tag} was not successful"     
    else
        docker push ghcr.io/converged-computing/lammps-time-fuse:${tag}
    fi
done
```

## Running Recording!

Note that I don't yet have a good way to cancel / exit from the filesystem when lammps finishes running. I think I can wait for the command to exit and do something (but haven't implemented it yet). For now it's easy enough to press control +c. Note that this should be run from the compat-lib root, or the binary moved here into a bin. Also note that we need to sanity check how far back the reax goes (I don't think it goes back as far as 2016).

```bash
for tag in $(oras repo tags ghcr.io/converged-computing/lammps-time-fuse)
  do
    if [[ -f "./bin/lammps-${tag}.out" ]]; then
       echo "Result for tag ${tag} already exists"
       continue
    fi
    echo "Running lammps for $tag"
    docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite
    if [[ "${retval}" != "0" ]]; then
        echo "Tag ${tag} was not successful"
        echo "docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite"
        break
    fi
done
```


Here are the individual commands I wound up running.

```bash
mkdir -p ./output

tag=stable_29Aug2024_update1
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_29Aug2024
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_29Aug2024
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite |& tee ./output/lammps-${tag}.out

# There was an input file change here - the reaxff didn't exist, but reaxc does.
# I remember this change from our converged computing work because it was 2023
tag=stable_2Aug2023_update4
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_27Jun2024
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_17Apr2024
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_2Aug2023_update3
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_7Feb2024_update1
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_7Feb2024
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_2Aug2023_update2
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_21Nov2023
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_2Aug2023_update1
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_2Aug2023
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_2Aug2023
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_15Jun2023
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_23Jun2022_update4
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_28Mar2023_update1
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_28Mar2023
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_23Jun2022_update3
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_8Feb2023
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_22Dec2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_23Jun2022_update2
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_3Nov2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_15Sep2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_23Jun2022_update1
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_3Aug2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_23Jun2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_23Jun2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_2Jun2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_4May2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_29Sep2021_update3
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_24Mar2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_17Feb2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_29Sep2021_update2
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_7Jan2022
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_14Dec2021
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_29Sep2021_update1
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_27Oct2021
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_29Sep2021
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_29Sep2021
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_20Sep2021
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_31Aug2021
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_30Jul2021
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_28Jul2021
docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_2Jul2021
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

# This is the first build that errored with:
# 'reax/c' is part of the USER-REAXC package which is not enabled in this LAMMPS binary
# I went back and added this build flag to ALL builds - it didn't break anything
tag=patch_27May2021
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_14May2021
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_8Apr2021
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_10Mar2021
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_10Feb2021
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_24Dec2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_30Nov2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_29Oct2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_29Oct2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_22Oct2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_9Oct2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_18Sep2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_24Aug2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_21Aug2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_21Jul2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_30Jun2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_15Jun2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_2Jun2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_5May2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_15Apr2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_19Mar2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_3Mar2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_3Mar2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_3Mar2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_27Feb2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_18Feb2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_4Feb2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_24Jan2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_9Jan2020
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_20Nov2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_30Oct2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_19Sep2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_7Aug2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_7Aug2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_6Aug2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_2Aug2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_19Jul2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_18Jun2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=stable_5Jun2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_5Jun2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

tag=patch_31May2019
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out

# First time to see:
# ERROR: Unknown pair style reax/c (/opt/lammps/src/force.cpp:246)
# This is the only one I could not build, because the flag was there so it must be a bug.
tag=stable_16Mar2018
docker run -v $PWD/bin:/compat --workdir /opt/lammps/examples/reax/HNS --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxc.hns -nocite |& tee ./output/lammps-${tag}.out
```

