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
    cd src  && \
    . /etc/profile && \ 
    make mpi && cp ./lmp_mpi /usr/local/bin

EXPOSE 22
WORKDIR /opt/lammps/examples/reaxff/HNS
