# jenkins-setup/jenkins-setup/README.md

# Jenkins Setup

This project provides a complete setup for a Jenkins controller using Docker. It includes a Docker Compose file, a Dockerfile for building a custom Jenkins image, and configuration files for Jenkins.

## Project Structure

```
jenkins-setup
├── docker-compose.yml      # Defines the services for the Jenkins setup
├── Dockerfile              # Custom Jenkins image with additional dependencies
├── jenkins
│   ├── casc.yaml          # Configuration as Code for Jenkins
│   ├── plugins.txt        # List of preinstalled Jenkins plugins
└── README.md              # Documentation for the project
```

## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

1. Clone the repository or download the project files.
2. Navigate to the project directory:
   ```
   cd jenkins-setup
   ```
3. Build the custom Jenkins image:
   ```
   docker build -t custom-jenkins .
   ```
4. Start the Jenkins services using Docker Compose:
   ```
   docker-compose up -d
   ```
5. Access Jenkins by navigating to `http://localhost:8080` in your web browser.

## Usage Guidelines

- The Jenkins controller will be available at `http://localhost:8080`.
- The default admin password can be found in the Jenkins logs or in the specified location in the `casc.yaml` file.
- The plugins listed in `plugins.txt` will be installed automatically during the Jenkins startup.

## Configuration

- Modify `casc.yaml` to customize Jenkins settings, including security and job configurations.
- Add or remove plugins in `plugins.txt` as needed.

## Contributing

Feel free to submit issues or pull requests for improvements or additional features.