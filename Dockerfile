FROM ubuntu:24.04

# Stop ubuntu-20 interactive options.
ENV DEBIAN_FRONTEND noninteractive
ARG TARGETPLATFORM
# Stop script if any individual command fails.
RUN set -e

# Define LLVM version.
ENV llvm_version=16.0.0

# Define home directory
ENV HOME=/home/SVF-tools

# Define dependencies.
ENV lib_deps="cmake g++ gcc git zlib1g-dev libncurses5-dev libtinfo6 build-essential libssl-dev libpcre2-dev zip libzstd-dev"
ENV build_deps="wget xz-utils git tcl software-properties-common gdb"

# Fetch dependencies.
RUN apt-get update --fix-missing
RUN apt-get install -y $build_deps $lib_deps

# Add deadsnakes PPA for multiple Python versions 
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN set -ex; \
    apt-get update && apt-get install -y python3.10-dev python3-pip \
            && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1;
RUN python3 -m pip install pysvf==1.0.0.1 -i https://test.pypi.org/simple/


# Fetch and build SVF source.
RUN echo "Downloading LLVM and building SVF to " ${HOME}
WORKDIR ${HOME}
RUN git clone "https://github.com/SVF-tools/SVF.git"
WORKDIR ${HOME}/SVF
RUN echo "Building SVF ..."
RUN bash ./build.sh

# Export SVF, llvm, z3 paths
ENV PATH=${HOME}/SVF/Release-build/bin:$PATH
ENV PATH=${HOME}/SVF/llvm-$llvm_version.obj/bin:$PATH
ENV SVF_DIR=${HOME}/SVF
ENV LLVM_DIR=${HOME}/SVF/llvm-$llvm_version.obj
ENV Z3_DIR=${HOME}/SVF/z3.obj
RUN ln -s ${Z3_DIR}/bin/libz3.so ${Z3_DIR}/bin/libz3.so.4

# Fetch and build Teaching-Software-Verification example.
WORKDIR ${HOME}
RUN git clone "https://github.com/SVF-tools/Teaching-Software-Verification.git"
WORKDIR ${HOME}/Teaching-Software-Verification
RUN echo "Building SVF-Teaching example ..."
RUN cmake -DCMAKE_BUILD_TYPE=MinSizeRel .
RUN make -j8
