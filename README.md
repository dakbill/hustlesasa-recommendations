# Hustlesasa Recommendations

## Overview

Recommendation engine software for HustleSasa's e-commerce platform.

## Features

- **Fast and Asynchronous**: Built with Python's asyncio for high performance.
- **Built-in Validation**: Request and response validation out of the box using Pydantic.
- **Scalable**: Designed for both small and large-scale applications.

## Prerequisites

- **Python**: Make sure you have Python 3.7 or higher installed.
- **Pip**: Ensure `pip` is installed for dependency management.
- Optional: `virtualenv` for isolated environments.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dakbill/hustlesasa-recommendations.git
   cd /path/to/hustlesasa-recommendations

2. Create a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
    ```
    pip install -r requirements.txt

4. Run the application:
    ```
    fastapi dev main.py

## Project Structure
    ```
    .
    ├── app
    │   ├── __init__.py
    │   ├── main.py          # Entry point of the application
    │   ├── test_main.py     # Unit tests
    │   ├── models.py        # Pydantic models
    ├── requirements.txt     # Project dependencies
    ├── README.md            # Project documentation
    └── .gitignore           # Files and directories to ignore in Git

## Usage

Once the application is running, navigate to the following URLs:


## Testing
    ```
    pytest


