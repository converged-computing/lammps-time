# LAMMPS Recording

We are going to build every tag of lammps that we built in the directory above... and add fuse and proot!
Then we can run a recording session! 

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
    echo "Running lammps for $tag"
    docker run -v $PWD/bin:/compat --security-opt apparmor:unconfined --device /dev/fuse --cap-add SYS_ADMIN -it ghcr.io/converged-computing/lammps-time-fuse:${tag} /compat/fs-record --out /compat/lammps-${tag}.out lmp -v x 2 -v y 2 -v z 2 -in ./in.reaxff.hns -nocite
    if [[ "${retval}" != "0" ]]; then
        echo "Tag ${tag} was not successful"     
    fi
done
```
