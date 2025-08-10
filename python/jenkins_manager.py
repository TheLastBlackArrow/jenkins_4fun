"""Jenkins Docker Manager: Manage Jenkins controller and agents using Docker Compose.

Provides cleanup, setup, and configuration automation for Jenkins environments.
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import docker
import yaml

# Ensure debug directory exists
DEBUG_DIR = Path(__file__).parent.parent / "debug"
DEBUG_DIR.mkdir(exist_ok=True)
LOG_FILE = DEBUG_DIR / "jenkins_manager.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(funcName)s:%(lineno)d] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
client = docker.from_env()


def cleanup() -> None:
    """Clean up Docker containers, images, volumes, networks, and build cache."""
    logging.info("Stopping all running containers...")
    for container in client.containers.list():
        try:
            container.stop()
        except docker.errors.APIError:
            logging.warning("Failed to stop container %s", container.name)

    logging.info("Removing all containers...")
    for container in client.containers.list(all=True):
        try:
            container.remove(force=True)
        except docker.errors.APIError:
            logging.warning("Failed to remove container %s", container.name)

    logging.info("Removing all unused images...")
    for image in client.images.list():
        try:
            client.images.remove(image.id, force=True)
        except docker.errors.APIError:
            logging.warning("Failed to remove image %s", image.id)

    logging.info("Removing all unused volumes...")
    for volume in client.volumes.list():
        try:
            volume.remove(force=True)
        except docker.errors.APIError:
            logging.warning("Failed to remove volume %s", volume.name)

    logging.info("Cleaning up build cache...")
    try:
        client.api.prune_builds()
    except docker.errors.APIError:
        logging.warning("Failed to prune build cache")

    logging.info("Removing all unused networks...")
    for network in client.networks.list():
        if network.name not in ["bridge", "host", "none"]:
            try:
                network.remove()
            except docker.errors.APIError:
                logging.warning("Failed to remove network %s", network.name)

    logging.info("Docker cleanup complete.")


def check_uv() -> None:
    """Check if 'uv' is installed."""
    logging.info("'uv' check started.")
    if not shutil.which("uv"):
        logging.info("'uv' is not installed. Please install it manually.")
        sys.exit(1)


def setup_ssh_key() -> tuple[str, str]:
    """Generate temporary SSH key pair and return private and public keys."""
    logging.info("Generating SSH key pair.")
    with tempfile.TemporaryDirectory() as tmp_key_dir:
        key_path = os.path.join(tmp_key_dir, "id_ed25519")
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", key_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        with open(key_path, "r", encoding="utf-8") as f:
            jenkins_ssh_private_key = f.read()
        with open(key_path + ".pub", "r", encoding="utf-8") as f:
            jenkins_agent_ssh_pubkey = f.read()
        logging.info("Temporary SSH key directory %s deleted.", tmp_key_dir)
    return jenkins_ssh_private_key, jenkins_agent_ssh_pubkey


def setup_jenkins_agents(agent_count: int, agent_service_name: str) -> None:
    """Start Jenkins agent containers."""
    logging.info("Starting %d %s containers...", agent_count, agent_service_name)
    subprocess.run(
        [
            "docker", "compose", "up", agent_service_name,
            "--build", "-d", "--scale", f"{agent_service_name}={agent_count}"
        ],
        check=True
    )


def collect_agents_and_generate_casc(agent_service_name: str) -> None:
    """Collect agent names and IPs, then generate casc.generated.yaml."""
    logging.info("Collecting agent names and IPs for service %s.", agent_service_name)
    agent_names = []
    agent_ips = []
    all_containers = client.containers.list(all=True)
    agent_containers = [c for c in all_containers if agent_service_name in c.name]
    for container in agent_containers:
        for _ in range(20):
            container.reload()
            if container.status == "running":
                break
            time.sleep(2)
        agent_names.append(container.name)
        networks = container.attrs['NetworkSettings']['Networks']
        ip = None
        if networks:
            for net_data in networks.values():
                ip = net_data.get('IPAddress')
                if ip:
                    break
        agent_ips.append(ip if ip else '')
    logging.info("Agent names: %s, Agent IPs: %s", agent_names, agent_ips)
    subprocess.run(
        [
            "python3", "jenkins/generate_casc.py",
            *agent_names, *agent_ips
        ],
        check=True
    )


def get_jenkins_url_from_env(controller_service_name: str) -> str | None:
    """Get Jenkins URL from environment variable or fallback to container IP."""
    logging.info("Getting Jenkins URL for controller service: %s", controller_service_name)
    controller_container = None
    for c in client.containers.list(all=True):
        if controller_service_name in c.name:
            controller_container = c
            break
    if controller_container:
        controller_container.reload()
        env_vars = controller_container.attrs.get('Config', {}).get('Env', [])
        jenkins_url = None
        for env in env_vars:
            if env.startswith('JENKINS_URL='):
                jenkins_url = env.split('=', 1)[1]
                break
        ip = controller_container.attrs['NetworkSettings']['IPAddress']
        logging.info("Jenkins URL: %s", jenkins_url)
        return jenkins_url if jenkins_url else f"http://{ip}:8080"
    logging.warning("Controller container not found for service: %s", controller_service_name)
    return None


def setup_jenkins_controller(controller_service_name: str) -> None:
    """Start Jenkins controller container."""
    logging.info("Starting %s controller...", controller_service_name)
    subprocess.run(
        ["docker", "compose", "up", "--build", "-d", controller_service_name],
        check=True
    )


def get_service_names(compose_file: Path) -> tuple[str, str]:
    """Extract agent and controller service names from docker-compose.yml."""
    logging.info("Reading service names from compose file: %s", compose_file)
    with open(compose_file, "r", encoding="utf-8") as f:
        compose = yaml.safe_load(f)
    agent_service_name = None
    controller_service_name = None
    for service in compose.get('services', {}):
        if 'agent' in service:
            agent_service_name = service
        if service == 'jenkins' or 'controller' in service:
            controller_service_name = service
    if not agent_service_name or not controller_service_name:
        logging.error("Could not find required service names in docker-compose.yml.")
        sys.exit(1)
    logging.info("Agent service: %s, Controller service: %s", agent_service_name, controller_service_name)
    return agent_service_name, controller_service_name


def create_jenkins_system(compose_file: Path, agent_count: int) -> None:
    """Create Jenkins system with agents and controller."""
    logging.info("Creating Jenkins system with compose file: %s and agent count: %d", compose_file, agent_count)
    check_uv()
    agent_service_name, controller_service_name = get_service_names(compose_file)

    jenkins_ssh_private_key, jenkins_agent_ssh_pubkey = setup_ssh_key()
    os.environ["JENKINS_SSH_PRIVATE_KEY"] = jenkins_ssh_private_key
    os.environ["JENKINS_AGENT_SSH_PUBKEY"] = jenkins_agent_ssh_pubkey

    setup_jenkins_agents(agent_count, agent_service_name)
    collect_agents_and_generate_casc(agent_service_name)
    setup_jenkins_controller(controller_service_name)
    logging.info("Jenkins agents and controller are up and casc.generated.yaml is updated.")
    jenkins_url = get_jenkins_url_from_env(controller_service_name)
    if jenkins_url:
        logging.info("Jenkins URL: %s", jenkins_url)


def main() -> None:
    """Main entry point for Jenkins Docker Manager."""
    logging.info("Starting Jenkins Docker Manager main function.")
    parser = argparse.ArgumentParser(description="Jenkins Docker Manager")
    parser.add_argument(
        "-c", "--clean", action="store_true",
        help="Cleanup Docker before creating Jenkins system"
    )
    parser.add_argument(
        "-cf", "--compose-file", type=Path, default="docker-compose.yml",
        help="Path to docker-compose.yml file"
    )
    parser.add_argument(
        "-n", "--num-agents", type=int, default=1,
        help="Number of Jenkins agents to create"
    )
    args = parser.parse_args()

    if args.num_agents == 0:
        logging.info("Number of Jenkins agents is 0. Exiting.")
        return

    if args.clean:
        cleanup()
        logging.info("Cleanup complete. Proceeding to Jenkins system setup...")
        if args.compose_file.exists():
            create_jenkins_system(args.compose_file, args.num_agents)
        else:
            logging.error("Compose file %s does not exist. Exiting.", args.compose_file)
            sys.exit(1)
    else:
        logging.info("No cleanup requested. Exiting.")


if __name__ == "__main__":
    main()
