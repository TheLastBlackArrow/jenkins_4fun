#!/usr/bin/env python3
import sys
from jinja2 import Environment, FileSystemLoader

args = sys.argv[1:]
if len(args) == 0 or len(args) % 2 != 0:
    print(
        "Usage: generate_casc.py <agent1-name> ... <agentN-name> <agent1-ip> ... <agentN-ip>",
        file=sys.stderr
    )
    sys.exit(1)

num_agents = len(args) // 2
agent_names = args[:num_agents]
agent_ips = args[num_agents:]
agents = [{"name": n, "ip": i} for n, i in zip(agent_names, agent_ips)]

# Setup Jinja2 environment to load the template from the jenkins directory
env = Environment(loader=FileSystemLoader('jenkins'))
template = env.get_template('casc.yaml')

rendered = template.render(agents=agents)

with open('jenkins/casc.generated.yaml', mode='w', encoding='utf-8') as f:
    f.write(rendered)

print(f"Rendered jenkins/casc.generated.yaml for {num_agents} agents.")
