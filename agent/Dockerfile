FROM jenkins/ssh-agent:latest-jdk21


# install python3, pip, pipx, uv, git, and git-lfs
RUN apt-get update && \
    apt-get install -y python3 python3-pip pipx git git-lfs && \
    pipx ensurepath && \
    pipx install uv

# install all python packages for machine learning using uv (via pipx)
ENV PATH="/root/.local/bin:$PATH"
RUN uv pip install --system numpy pandas scikit-learn tensorflow keras matplotlib seaborn
