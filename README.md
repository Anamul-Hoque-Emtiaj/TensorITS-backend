# tits-backend

## Setup

### Prerequisites

Make sure you have the following installed on your system:

- Python 3.10
- pip (Python package installer)

### Setup Instructions

1. Clone the repository:

    ```bash
    git clone https://github.com/Anamul-Hoque-Emtiaj/tits-backend.git
    ```

2. Navigate to the project directory:

    ```bash
    cd tits-backend
    ```

3. Run the `create_venv.bat` script to create a virtual environment:

    ```bash
    create_venv.bat
    ```

    This script will create a virtual environment named `venv` and install the required dependencies.

4. Activate the virtual environment:

    On Windows:

    ```bash
    venv\Scripts\activate
    ```

    On Linux/Mac:

    ```bash
    source venv/bin/activate
    ```
5. Run the development server:

    ```bash
    python manage.py runserver
    ```