# Kiyabo Duka

Kiyabo Duka is a Django-based retail management system designed to streamline operations for retail businesses. This document provides comprehensive information about the system's features, setup, and usage.

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Contributing](#contributing)
6. [License](#license)

## Features
- **User Management**: Built-in authentication for users and staff.
- **Product Management**: Track inventory, categorize products, and manage stock levels.
- **Sales Management**: Handle transactions, sales reports, and customer receipts.
- **Analytics and Reporting**: Access to detailed reports on sales, inventory, and user activity.

## Installation
### Requirements
- Python 3.8 or higher
- Django 3.2 or higher

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/kiyaboapp/duka-letu.git
   cd duka-letu
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser for administrative access:
   ```bash
   python manage.py createsuperuser
   ```
5. Start the server:
   ```bash
   python manage.py runserver
   ```

## Configuration
Configuration files can be found in the `config` directory. You can adjust settings according to your environment.

## Usage
Once the server is running, navigate to `http://127.0.0.1:8000/` to access the application. Use the superuser credentials to log in and manage the system.

## Contributing
Contributions are welcome! Please read the CONTRIBUTING.md file for guidelines on contributing to the project.

## License
This project is licensed under the MIT License. See the LICENSE file for more details. 

---

For more information, please visit the official documentation or refer to the project repository.