ARG tag=jammy
FROM ubuntu:${tag}
ENV DEBIAN_FRONTEND=noninteractive
ARG LAMMPS_VERSION=develop
ENV LAMMPS_VERSION=${LAMMPS_VERSION}
RUN apt-get update && \
    apt-get install -y fftw3-dev fftw3 pdsh libfabric-dev libfabric1 \
        dnsutils telnet strace cmake git g++ \
        mpich

WORKDIR /opt/
RUN git clone --depth 1 --branch ${LAMMPS_VERSION} https://github.com/lammps/lammps.git /opt/lammps && \
    cd /opt/lammps && \
    mkdir build && \
    cd build && \
    . /etc/profile && \ 
    cmake ../cmake -DPKG_USER-REAXC=yes -DCMAKE_INSTALL_PREFIX:PATH=/usr -DPKG_REAXFF=yes -DBUILD_MPI=yes -DPKG_OPT=yes -DFFT=FFTW3 -DCMAKE_PREFIX_PATH=/usr/lib/mpich -DCMAKE_PREFIX_PATH=/usr/lib/x86_64-linux-gnu && \
    make && \
    make install

EXPOSE 22
WORKDIR /opt/lammps/examples/reaxff/HNS
