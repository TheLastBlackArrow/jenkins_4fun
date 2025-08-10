# Jenkins Setup

This project provides a complete setup for a Jenkins controller using Docker. It includes a Docker Compose file, Dockerfiles for building images, Jenkins Configuration-as-Code templates, and automation scripts for setup and cleanup.

## Project Structure

```
jenkins_4fun
├── docker-compose.yml                # Defines the services for the Jenkins setup
├── Dockerfile                        # Custom Jenkins image with additional dependencies
├── jenkins
│   ├── casc.yaml                     # Configuration as Code for Jenkins
│   ├── plugins.txt                   # List of preinstalled Jenkins plugins
│   └── generate_casc.py              # Python script to generate casc config
├── python
│   └── jenkins_manager.py            # Main Python automation script
├── shell
│   └── cleanup.sh                    # Shell script for Docker cleanup
│   └── startUp_script.sh             # Shell script for startup Jenkins system
└── README.md                         # Documentation for the project
```

## Prerequisites

- Docker
- Docker Compose
- Python 3.12+
- `uv` Python package manager (required by automation scripts)

## Setup Instructions

1. Clone the repository or download the project files.
2. Navigate to the project directory:
   ```
   cd /<home_drive>/jenkins_4fun
   ```
3. Build the custom Jenkins image (optional — the automation scripts will build as needed):
   ```
   docker build -t custom-jenkins .
   ```
4. Start the Jenkins services using Docker Compose:
   ```
   docker compose up -d
   ```
5. Access Jenkins by navigating to `http://localhost:8080` in your web browser.

## Automation Scripts Usage

### Python Automation

The main automation script is located at `python/jenkins_manager.py`. It can be used to clean up Docker resources and set up Jenkins agents and controller automatically.

**Usage:**
```sh
uv venvs --python=3.12
uv pip install python/requirements.txt
python3 python/jenkins_manager.py --clean --compose-file docker-compose.yml --num-agents 2
```

- `--clean`: Cleans up Docker containers, images, volumes, and networks before setup.
- `--compose-file`: Path to your `docker-compose.yml` file.
- `--num-agents`: Number of Jenkins agent containers to start.

### Shell Scripts

You can run the included shell scripts for a manual workflow or quick development runs:
```sh
bash shell/startUp_script.sh
bash shell/clean.sh
```

## Guidelines for End Users

- Ensure Docker and Docker Compose are running before executing any setup or cleanup scripts.
- Use the Python automation script for a streamlined Jenkins setup and cleanup process.
- Customize `jenkins/casc.yaml` and `jenkins/plugins.txt` as needed for your Jenkins configuration.
- After running the automation script, check the output for the Jenkins URL and access credentials.
- For troubleshooting, inspect logs in the Jenkins container or review the output of the automation script.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Contributing

Feel free to submit issues or pull requests for improvements or additional features.