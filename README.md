# Store Monitoring Backend

This repository contains the implementation of a backend service that generates uptime and downtime reports for restaurants based on their business hours and active/inactive polling data. The service is designed to handle dynamic data, enabling restaurant owners to monitor their stores' performance and receive detailed reports on demand.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [System Design](#system-design)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
  - [Trigger Report Endpoint](#trigger-report-endpoint)
  - [Get Report Endpoint](#get-report-endpoint)
- [Data Processing Logic](#data-processing-logic)
- [Code Structure](#code-structure)
- [Assumptions](#assumptions)
- [Improvements](#improvements)
- [Demo](#demo)
- [Output](#output)

## Tech Stack

- **Language**: Python
- **Framework**: Django
- **Database**: MySQL
- **Other Dependencies**:
  - Django REST framework for API development
  - Django ORM for database interactions
  - Pandas
  - pytz for timezone handling
  - Celery for asynchronous task management
  - Redis for Celery backend

## Features

- **Dynamic Report Generation**: The system computes the uptime and downtime of stores based on active/inactive status during business hours and provides comprehensive reports.
- **Poll-based Architecture**: Data is ingested hourly, and the report generation process can be triggered and tracked asynchronously.
- **Extrapolation Logic**: Missing status data between polling periods is filled with interpolated data to compute uptime and downtime accurately.
- **Timezone Handling**: The system handles multiple timezones to ensure business hours and polling timestamps align correctly.

## System Design

1. **Database Storage**: All data from the CSV files are stored in relational tables in the database. The system supports dynamic updates to these tables as new polling data comes in.
2. **Report Triggering & Polling**:
   - `/trigger_report` API starts the report generation process, which processes the stored data.
   - `/get_report` API checks the report's status or fetches the CSV output when ready.
3. **Data Synchronization**: Polling data, store business hours, and timezones are all synchronized to ensure uptime/downtime is computed based on accurate local business times.

## Installation

### Requirements

- Python 3.10+
- MySQL 8.0+
- Redis 6.0+
- Git
- Virtualenv

### Configuration

- Export the following environment variables for database configuration:
  ```bash
  export MYSQL_USER={your-mysql-username}
  export MYSQL_PASSWORD={your-mysql-password}
  export MYSQL_HOST={your-mysql-host}
  export MYSQL_PORT={your-mysql-port}
  export MYSQL_DB={your-mysql-db}
  ```
- Ensure Redis is running on the default port `6379`.

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/{your-repo-name}.git
   cd {your-repo-name}
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up MySQL database and make migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the Celery worker:
   ```bash
   celery -A app.background worker --loglevel=INFO --concurrency=1 -n worker1@h
   ```
5. Start the Django server:
   ```bash
   python manage.py runserver
   ```

## Usage

Once the server is up and running, you can access the following APIs:

## API Documentation:

### Trigger Report Endpoint

- Endpoint: `/trigger_report`
- Method: GET
- Description: Triggers the report generation process asynchronously.
- Response: `report_id` which can be used to query the report status.
- Sample Request:
  ```bash
  curl http://localhost:8000/trigger_report
  ```
- Sample Response:
  `json
{
    "report_id": "abc123"
}
`

### Get Report Endpoint

- Endpoint: `/get_report`
- Method: GET
- Description: Fetches the report status or the CSV output when ready.
- Query Parameters:
  - `report_id`: The unique identifier for the report.
- Response: The report status or the CSV output.
- Sample Request:
  ```bash
  curl http://localhost:8000/get_report?report_id=abc123
  ```
- Sample Response:
  ```json
  {
    "status": "Running"
  }
  ```

## Data Processing Logic

### Data Models:

- **Store**: Represents a restaurant store with the following fields:

  - `id`: Unique identifier
  - `store_id`: Store identifier
  - `timezone`: Timezone of the store

- **StoreHours**: Represents the business hours of a store with the following fields:

  - `id`: Unique identifier
  - `store`: Foreign key to the `Store` model
  - `day_of_week`: Day of the week (0-6, where 0 is Monday)
  - `start_time_local`: Opening time in local time
  - `end_time_local`: Closing time in local time

- **StoreStatus**: Represents the status of a store at a given timestamp with the following fields:
  - `id`: Unique identifier
  - `store`: Foreign key to the `Store` model
  - `timestamp`: Timestamp of the status
  - `status`: Boolean indicating whether the store is active (True) or inactive (False)

### Report Generation:

1. **Data Retrieval**: Fetch store hours, store status, and store timezone data from the database.
2. **Loading Data**: Loading the data into Python data structures for processing.
3. **Calculating Uptime/Downtime**:
   - For each day of the week, generate the time intervals of 15 minutes between opening and closing hours.
   - Fill in the status data for that particular day
   - Interpolate the missing status data between timestamps with data
   - Calculate the uptime and downtime based on the active/inactive status.
4. **Output Generation**: Generate a CSV file with the uptime and downtime data for each store.

## Code Structure

```text
.
├── README.md
├── app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── background
│   │   ├── celery.py
│   │   ├── params.py
│   │   ├── task_handler.py
│   │   ├── task_signal.py
│   │   └── tasks.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_load_data.py
│   │   ├── 0003_report.py
│   │   ├── 0004_alter_report_report.py
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── data
│   ├── store_hours.csv
│   ├── store_status.csv
│   └── store_timezones.csv
├── manage.py
├── report.csv
├── requirements.txt
└── test.py
```

## Assumptions

- The polling data is ingested hourly, and the report generation process is triggered manually.

## Improvements

- Implement a scheduler to trigger the report generation process automatically.
- Add support for real-time data ingestion and processing.
- Enhance the report generation process to handle large datasets efficiently.

## Demo

A brief demo of the system can be found [here](https://drive.google.com/file/d/1SphijZIYT6xqq15zH83b5sPSkYUpKkQn/view?usp=sharing).

## Output

Sample CSV output can be found [here](report.csv).
