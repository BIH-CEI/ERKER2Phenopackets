# PythonTemplate
This repository contains a simple template for Python repositories, including actions and a .gitignore file. The actions include linting using ruff and automatic test execution using pytest on merging to the main branch.

You can also add a badge like this one to your README.md file:
[![Unit Tests and Code Style](https://github.com/frehburg/PythonTemplate/actions/workflows/python-app.yaml/badge.svg)](https://github.com/frehburg/PythonTemplate/actions/workflows/python-app.yaml)

## Branch Protection
- Go to Settings -> Branches -> Add Branch protection rule
- Enter "main" as branch name pattern
- Check "Require a pull request before merging"
  - Check "Require approvals" and select at least one reviewer
- Check "Require status checks to pass before merging"
- (Optional:) Check "Require signed commits" if you are using SSH to sign your commits
- Check "Require linear history"
- Make sure to NOT check "Allow force pushes" and "Allow deletions"

See here a template for your README

# Project Name

Brief description of your project.

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Project Description

A brief overview of your project and its purpose.

## Features

List the key features of your project.

## Getting Started

Instructions on how to set up and run your project locally.

### Prerequisites

List any software, libraries, or dependencies that need to be installed before setting up the project.

### Installation

Step-by-step instructions on how to install and set up your project.

## Features

Provide examples and explanations of how your project can be used. Include code snippets or screenshots if necessary.

## Contributing

Guidelines for contributing to your project. Include information about how others can contribute, submit issues, and create pull requests.

## License

Specify the license under which your project is distributed.

## Acknowledgements

Credit any individuals, resources, or tools that have inspired or helped your project.

---

**Note:** Customize the sections, content, and formatting to fit your project's needs. Remember to replace placeholders with actual information.
