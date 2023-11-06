# PushAdminer

Welcome to the PushAdminer GitHub repository! PushAdminer is built as part of a research projec that focuses on identifying ads (malicious) that are served by websites through push notifications. 
- **Research Paper:** [PushAdminer Research Paper](https://dl.acm.org/doi/10.1145/3419394.3423631)
  
## Project Overview
The rapid growth of online advertising has fueled the growth of ad-blocking software, such as new ad-blocking and privacy-oriented browsers or browser extensions. In response, both ad publishers and ad networks are constantly trying to pursue new strategies to keep up their revenues. To this end, ad networks have started to leverage the Web Push technology enabled by modern web browsers. As web push notifications (WPNs) are relatively new, their role in ad delivery has not yet been studied in depth. Furthermore, it is unclear to what extent WPN ads are being abused for malvertising (i.e., to deliver malicious ads). In this paper, we aim to fill this gap. Specifically, we propose a system called PushAdMiner that is dedicated to (1) automatically registering for and collecting a large number of web-based push notifications from publisher websites, (2) finding WPN-based ads among these notifications, and (3) discovering malicious WPN-based ad campaigns.

Using PushAdMiner, we collected and analyzed 21,541 WPN messages by visiting thousands of different websites. Among these, our system identified 572 WPN ad campaigns, for a total of 5,143 WPN-based ads that were pushed by a variety of ad networks. Furthermore, we found that 51% of all WPN ads we collected are malicious, and that traditional ad-blockers and URL filters were mostly unable to block them, thus leaving a significant abuse vector unchecked.


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
