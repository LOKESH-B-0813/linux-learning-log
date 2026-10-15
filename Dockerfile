FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 git curl nano procps iproute2 less ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m learner
USER learner
WORKDIR /home/learner/linuxlab
COPY --chown=learner . .
CMD ["python3", "learn.py", "--no-git"]
