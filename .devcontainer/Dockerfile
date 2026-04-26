ARG VARIANT="base:bookworm"

FROM mcr.microsoft.com/devcontainers/${VARIANT}

ARG WORKSPACE=$WORKSPACE

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install --no-install-recommends \
        sqlite3 \
        git-flow
