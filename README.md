# LAMMPS over Time

Let's try to build LAMMPS, specifically the reax app, over time, and see how it changes.
We will use the same Dockerfile with different versions to clone. This top level directory will
build lammps base containers, and [fuse](fuse) will provide logic to install fuse and proot
for recording.

# Building Containers

Let's get the tags. I exported my GitHub token to the environment here.
I could just write a Python script, but I'm being lazy.

```bash
mkdir -p ./releases
for page in $(seq 1 4)
 do
  curl -L \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    https://api.github.com/repos/lammps/lammps/releases?page=${page} > releases/${page}.json
    sleep 2
done
```

Now do builds from the tags. We are first going to try and build as many as we can with cmake.

```bash
for filename in $(ls ./releases)
  do
  for tag in $(cat ./releases/$filename | jq -r .[].tag_name)
    do
     echo "Building tag $tag"
     docker build -f Dockerfile.cmake --build-arg LAMMPS_VERSION=${tag} -t ghcr.io/converged-computing/lammps-time:${tag} .
     retval=$?
     if [[ "${retval}" != "0" ]]; then
         echo "Tag ${tag} was not successful"     
     else
      docker push ghcr.io/converged-computing/lammps-time:${tag}
     fi
  done
done
```

Now we need an older cmake (and ubuntu) for this next set (I tried focal and it didn't work).

```bash
for tag in $(cat cmake-older-version.txt)
  do
  docker build -f Dockerfile.cmake --build-arg LAMMPS_VERSION=${tag} --build-arg tag=bionic -t ghcr.io/converged-computing/lammps-time:${tag} .
   if [[ "${retval}" != "0" ]]; then
    echo "Tag ${tag} was not successful"     
  else
    docker push ghcr.io/converged-computing/lammps-time:${tag}
  fi
done
```

Next fall back to building from source method.

```bash
for tag in $(cat non-cmake-tags.txt)
  do
  docker build --build-arg LAMMPS_VERSION=${tag} --build-arg tag=bionic -t ghcr.io/converged-computing/lammps-time:${tag} .
   if [[ "${retval}" != "0" ]]; then
    echo "Tag ${tag} was not successful"     
  else
    docker push ghcr.io/converged-computing/lammps-time:${tag}
  fi
done
```

