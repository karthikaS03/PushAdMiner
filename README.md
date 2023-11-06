# PushAdminer

Welcome to the PushAdminer GitHub repository! PushAdminer is built as part of a research projec that focuses on identifying ads (malicious) that are served by websites through push notifications. 

## Project Overview

- **GitHub Repository:** [PushAdminer GitHub](https://github.com/karthikaS03/PushAdMiner)
- **Research Paper:** [PushAdminer Research Paper](https://dl.acm.org/doi/10.1145/3419394.3423631)

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

Follow these steps to set up PushAdminer on your system.

### Prerequisites

Before you begin, make sure you have the following prerequisites installed:

- Docker: You need Docker installed on your machine. You can download it from [Docker's official website](https://www.docker.com/get-started).

### Installation

1. **Pull the Docker image:**
   ```shell
   docker pull dockerammu/docker_puppeteer_chromium_xvfb:ver7
   ```
   
2. **Set up the database:**
    Use the provided database creation script to set up your PostgreSQL server. You can find the script in the project repository.

3. **Modify configuration files:**
  Update the configuration parameters in the docker_config (docker_config.py) file as well as the database configuration file (path: /DataCollector/database/config.py) according to your requirements.

4. **Run the script:**
   ```shell
   python visit_urls.py
   ```

### Usage
The visit_urls.py script initiates the crawling process using Docker containers and collects notifications from websites. Make sure you have completed the installation steps before running this script.

### Contributing
If you would like to contribute to PushAdminer, feel free to fork the repository and submit a pull request with your changes. We welcome contributions that can enhance the project.

### License
PushAdminer is distributed under the MIT License. For detailed information, please refer to the LICENSE file.

Thank you for your interest in PushAdminer. If you have any questions or encounter issues, please open an issue in the GitHub repository for assistance.

### Citation
```bibtex
@inproceedings{10.1145/3419394.3423631,
author = {Subramani, Karthika and Yuan, Xingzi and Setayeshfar, Omid and Vadrevu, Phani and Lee, Kyu Hyung and Perdisci, Roberto},
title = {When Push Comes to Ads: Measuring the Rise of (Malicious) Push Advertising},
year = {2020},
isbn = {9781450381383},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3419394.3423631},
doi = {10.1145/3419394.3423631},
pages = {724–737},
numpages = {14},
location = {Virtual Event, USA},
series = {IMC '20}
}
