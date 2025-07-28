#!/bin/bash

# Ask user for number of Jenkins agents
read -p "Enter the number of Jenkins agents to create: " AGENT_COUNT

# Generate SSH key (ed25519) in a temporary location on the host
TMP_KEY_DIR=$(mktemp -d)
ssh-keygen -t ed25519 -N "" -f "$TMP_KEY_DIR/id_ed25519"
JENKINS_SSH_PRIVATE_KEY=$(cat "$TMP_KEY_DIR/id_ed25519")
JENKINS_AGENT_SSH_PUBKEY=$(cat "$TMP_KEY_DIR/id_ed25519.pub")

# Clean up temporary SSH key directory
rm -rf "$TMP_KEY_DIR"
echo "Temporary SSH key directory $TMP_KEY_DIR deleted."
export JENKINS_SSH_PRIVATE_KEY="$JENKINS_SSH_PRIVATE_KEY"
export JENKINS_AGENT_SSH_PUBKEY="$JENKINS_AGENT_SSH_PUBKEY"

# Start all agent containers at once using Docker Compose scaling
docker compose up jenkins-agent --build -d --scale jenkins-agent=$AGENT_COUNT

# Wait for agents to be up and collect their IPs
AGENT_NAMES=()
AGENT_IPS=()
AGENT_CONTAINERS=$(docker compose ps -q jenkins-agent)
for CONTAINER_ID in $AGENT_CONTAINERS; do
  AGENT_NAME=$(docker inspect --format '{{.Name}}' $CONTAINER_ID | sed 's|/||')
  AGENT_IP=""
  for attempt in {1..10}; do
    AGENT_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID 2>/dev/null)
    if [[ -n "$AGENT_IP" ]]; then
      break
    fi
    sleep 1
  done
  AGENT_NAMES+=("$AGENT_NAME")
  AGENT_IPS+=("$AGENT_IP")
done

# Generate casc.generated.yaml once with all agent names and IPs
python3 jenkins/generate_casc.py "${AGENT_NAMES[@]}" "${AGENT_IPS[@]}"

# Start Jenkins controller after agents and casc.generated.yaml are ready
docker compose up --build -d jenkins

echo "Jenkins agents and controller are up and casc.generated.yaml is updated."

