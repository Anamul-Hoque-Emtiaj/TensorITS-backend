# TensorITS-backend

Tensor Insight Training System - Learn and Practice Tensor Manipulation by solving Puzzles. Write PyTorch code to get the expected Tensor from the Input Tensor.

**Note:** This repository contains the local version backend code of our project (my parts). You can find both the frontend and backend code of the deployed version [here](https://github.com/zarifikram/Tensor-Insight-Training-System).

## Setup

### Prerequisites

Make sure you have the following installed on your system:

- Python 3.10
- pip (Python package installer)

### Setup Instructions for windows

1. Clone the repository:

    ```bash
    git clone https://github.com/Anamul-Hoque-Emtiaj/TensorITS-backend.git
    ```

2. Navigate to the project directory:

    ```bash
    cd TensorITS-backend
    ```

3. Run the `create_venv.bat` script to create a virtual environment:

    ```bash
    create_venv.bat
    ```

    This script will create a virtual environment named `venv` and install the required dependencies.

4. Activate the virtual environment:

    ```bash
    call venv\Scripts\activate
    ```
5. Run the development server:

    ```bash
    python manage.py runserver
    ```

## Frontend
- **Technology Stack:**
  - React JS
  - Tailwind CSS
  - HTML
- **Deployment:**
  - Frontend deployed on Firebase

## Backend
- **Technology Stack:**
  - Django Rest Framework
  - PostgreSQL DB
- **Deployment:**
  - Backend deployed on Azure Kubernetes Service (AKS)

## Cloud Services
  - **Firebase Authentication System:** Used for user authentication(supports email-password and one-click Google authentication)
  - **Azure Database for PostgreSQL:** Managed PostgreSQL database
  - **Azure Storage Account:** Cloud storage for media and static files
  - **Azure Container Registry:** Container image registry
  - **Azure Kubernetes Service (AKS):** Used for deploying and managing backend services

## Others
  - **Version Control:** Git and Github
  - **CI-CD:** Github Actions workflow

## Features
- **Puzzle Sources:**
  - Random Generation
  - User Contribution

- **Puzzle-Set:**
  - Pagination
  - Filtering

- **Puzzle:**
  - User Submission
  - Comment-Reply
  - Upvote/Downvote

- **Challenge Modes and Leaderboards:**
  - Time Mode
  - Quantity Mode
  - Custom Mode

- **One V One Challenge:**
  - Real-time Opponent’s Update Through Pop-up

- **Contest:**
  - Daily Auto-Generated Contest
  - User Created Custom Contest
  - Contest Leaderboard

- **Discussion Forum:**
  - Questions
  - Answer
  - Reply
  - Upvote/Downvote

- **User:**
  - Signin/ Signup
  - Basic User operation
  - User XP and Level
  - User Achievements

## _Frontend_Link_ [_*Here*_](https://tensor-its.web.app/)
## _Backend_Link_ [_*Here*_](http://172.212.122.116/)

## Project Diagram
### Backend CI/CD Diagram
![CI_CD](https://github.com/Anamul-Hoque-Emtiaj/TensorITS-backend/blob/main/diagrams/ci_cd_pipeline.jpg)

### High Level Architecture Diagram
![Architecture](https://github.com/Anamul-Hoque-Emtiaj/TensorITS-backend/blob/main/diagrams/architecture_diagram.jpg)