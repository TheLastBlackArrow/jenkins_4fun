FROM jenkins/ssh-agent:latest-jdk21

# install python3, git, and uv only
RUN apt-get update && \
    apt-get install -y python3 git curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# copy requirements file and install with uv in a venv
COPY requirements.uv.txt /requirements.uv.txt
RUN uv venv /opt/uv-venv \
    && uv pip install --python /opt/uv-venv/bin/python -r /requirements.uv.txt
ENV PATH="/opt/uv-venv/bin:$PATH"

