# 🍼 Baby Feed Tracker: End-to-End Data Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python >=3.14](https://img.shields.io/badge/python-%3E%3D3.14-blue.svg)](https://www.python.org/) [![pandas >=2.3.3](https://img.shields.io/badge/pandas-%3E%3D2.3.3-blue.svg)](https://pypi.org/project/pandas/) [![plotly >=6.5.0](https://img.shields.io/badge/plotly-%3E%3D6.5.0-blue.svg)](https://pypi.org/project/plotly/) [![dash >=3.3.0](https://img.shields.io/badge/dash-%3E%3D3.3.0-blue.svg)](https://pypi.org/project/dash/) [![pydantic >=2.12.5](https://img.shields.io/badge/pydantic-%3E%3D2.12.5-blue.svg)](https://pypi.org/project/pydantic/) [![dash-bootstrap-components >=2.0.4](https://img.shields.io/badge/dash--bootstrap--components-%3E%3D2.0.4-blue.svg)](https://pypi.org/project/dash-bootstrap-components/)

**A production-grade ETL pipeline and interactive Dash application for multi-child nutritional tracking.**

https://github.com/user-attachments/assets/de07eabc-7789-481e-aa2b-2742890e4be2

An end-to-end Python application designed to track and visualize infant feeding schedules using an object-oriented architecture.

- [🍼 Baby Feed Tracker: End-to-End Data Pipeline](#-baby-feed-tracker-end-to-end-data-pipeline)
  - [🎯 Project Objective](#-project-objective)
  - [⚙️ The Data Pipeline](#️-the-data-pipeline)
  - [📊 Visualization \& UI](#-visualization--ui)
  - [✨ Features](#-features)
  - [📥 Installation](#-installation)
    - [Option 1: Using `uv` (Recommended)](#option-1-using-uv-recommended)
    - [Option 2: Using Python venv + pip](#option-2-using-python-venv--pip)
  - [⚙️ Configuration](#️-configuration)
    - [Configuration Schema](#configuration-schema)
    - [Adding Your Data Files](#adding-your-data-files)
  - [📂 Project Structure](#-project-structure)
  - [📋 Sample Data Format](#-sample-data-format)
  - [🚀 Usage](#-usage)
  - [Data Validation \& Error Logging](#data-validation--error-logging)
    - [Row-Level Error Tracking](#row-level-error-tracking)
    - [Example Error Output](#example-error-output)
    - [Error Logging Logic](#error-logging-logic)
  - [🎨 Dashboard Overview](#-dashboard-overview)
    - [**Home Page (Daily Feed Summary)**](#home-page-daily-feed-summary)
    - [**Child Deep-Dive (Individual Feed Review)**](#child-deep-dive-individual-feed-review)
    - [**Circadian Analytics (Day vs. Night)**](#circadian-analytics-day-vs-night)
  - [💾 Data Export](#-data-export)
    - [Export Options](#export-options)
    - [Export Contents](#export-contents)
  - [🛠️ Requirements](#️-requirements)
    - [🐍 Python Environment](#-python-environment)
    - [📦 Key Dependencies](#-key-dependencies)
  - [🧪 Running Tests](#-running-tests)
  - [📜 License](#-license)
  - [🤝 Contributing](#-contributing)


## 🎯 Project Objective
The primary goal of this project is to demonstrate a **production-grade Python workflow**. It serves as a blueprint for an end-to-end process taking raw data through a structured pipeline—leveraging Object-Oriented Programming (OOP)—and delivering actionable insights via an interactive web dashboard.

## ⚙️ The Data Pipeline
The core logic is divided into four distinct stages to ensure data integrity and modularity:

1. **Data Loading:** Ingesting raw feeding logs from source files.
2. **Data Cleaning:** Handling missing values and normalizing timestamps for consistency.
3. **Pydantic Validation (v2.12):** Enforcing strict data schemas to ensure the pipeline remains robust and type-safe.
4. **Data Transformation:** Processing raw logs into analytical datasets (e.g., calculating daily volumes or feeding intervals).

The **DataPipeline** class orchestrates this flow on a per-child basis, leveraging **Pandas** for high-performance transformations and **Pydantic** for rigorous schema enforcement.

## 📊 Visualization & UI
The processed data is served through a **Plotly Dash** interface. By utilizing **Plotly Express**, the project generates interactive visualizations that allow users to:
* Monitor feeding trends over time.
* Analyze volume distributions.
* Gain quick, data-driven insights into a baby's schedule.

Application styling and interface are developed with **Dash Boostrap Components**.

## ✨ Features

- Create and manage feeding schedules
- Track feeding times and amounts
- Monitor baby nutrition patterns

## 📥 Installation

### Option 1: Using `uv` (Recommended)

```bash
git clone <repository-url>
uv sync
```

### Option 2: Using Python venv + pip

```bash
git clone <repository-url>
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .
```

## <a name="configuration"></a>⚙️ Configuration

This project uses **Pydantic Settings** to manage multi-child configurations. To set up which children you want to track, create a `.env` file in the project root:

```env
CHILDREN='
  [{"name": "Child 1", "file_name": "file 1.xlsx", "dob": "<dob 1>"}, 
   {"name": "Child 2", "file_name": "file 2.xlsx", "dob": "dob 2"}]'
```

### Configuration Schema
Each child requires the following fields in the `CHILDREN` JSON array:

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | string | Display name for the child (used in dashboards and exports) |
| `file_name` | string | Name of the feeding log file (without path; placed in `data/` folder) |
| `dob` | date (YYYY-MM-DD) | Date of birth for age-based analytics |

### Adding Your Data Files
Place your feeding log files in the `data/` folder with the exact filename specified in the configuration. Supported formats:
- **Excel**: `.xlsx` files
- **CSV**: `.csv` files

Ensure your feeding logs contain the required columns matching the `FeedingData` schema (see [Sample Data Format](#-sample-data-format)).

## 📂 Project Structure

Within the repo sits the following structure:

- `src/` contains
    - `app/` — Dash app factory with Plotly charts and interactive dashboard
    - `models/` — Pydantic data schemas
    - `pipeline/` — ETL orchestration (load, clean, validate, transform)
- `reporting/` — Excel report outputs (not tracked in Git)
- `tests/` — Unit tests
- `main.py` — Execution entry point

## 📋 Sample Data Format

The pipeline expects feeding logs with the following columns matching the `FeedingData` schema:

| Column | Type | Example |
| :--- | :--- | :--- |
| feed_start_time | datetime | 2025-12-24 10:30:00 |
| activity | string | Feeding |
| type | string | Bottle |
| feed_volume_ml | float | 120.5 |
| units | string | ml |

**Supported values:**
- `activity`: `Feeding`
- `type`: `Left`, `Right`, `Bottle`

Place your feeding log file in the `data/` folder (`.xlsx` or `.csv` format):

```bash
data/file_name.xlsx
```

For each child you will need to provide a **name** and a **date of birth**.

## 🚀 Usage

Run the data pipeline and launch the interactive dashboard:

```bash
python main.py
```

The dashboard will be available at `http://127.0.0.1:8050` by default.

## Data Validation & Error Logging

The pipeline employs a "Graceful Failure" strategy for data validation using Pydantic. When records fail validation (e.g., missing fields, incorrect data types, or invalid values), they are not lost. Instead, they are captured, formatted, and stored in a dedicated error reporting DataFrame.

### Row-Level Error Tracking
For every record that triggers a `ValidationError`, the pipeline:
1.  **Extracts the raw record data**: Keeps the original values for context.
2.  **Counts the issues**: Records the total number of validation failures for that specific row.
3.  **Formats error details**: Concatenates multiple errors into a numbered, readable list identifying exactly which field failed and why.

This allows for easy auditing and data cleaning without interrupting the processing of valid records.

### Example Error Output
If the pipeline encounters invalid data, the resulting `error_df` will structured as follows:

| Name | Event | Value | ... | total_errors | error_details |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Baby A | Feeding | "None" | ... | 2 | 1) Value: input is not a valid float <br> 2) Time: field required |
| Baby B | Sleep | 12.5 | ... | 1 | 1) Date: invalid date format |

### Error Logging Logic
The following logic in `data_pipeline.py` ensures that every validation hurdle is documented:

```python
except ValidationError as e:
    # Format multiple errors into a single string for the record
    details = "\n".join(
        f"{i}) {err['loc'][0]}: {err['msg']}"
        for i, err in enumerate(e.errors(), 1)
    )

    # Append the original record + error metadata to the error list
    error_records.append({
        **record_dict,
        'total_errors': e.error_count(),
        'error_details': details
    })

# Convert to DataFrame for export/analysis
error_df = pd.DataFrame(error_records)
```

The `error_df` can the be exported via the `export_data` method detailed below.

## 🎨 Dashboard Overview

The dashboard provides multiple views for analyzing feeding patterns across one or multiple children:

### **Home Page (Daily Feed Summary)**
A high-level aggregated summary designed for parents tracking multiple children simultaneously.
* **Unified Feed Stats:** A single view of total volumes by day and last-feed timestamps across all profiles.
* **Rolling Trends:** Overlay of rolling averages to see how different infants are progressing relative to one another.
* **Global Navigation:** One-tap access to switch between deep-dive views for each child.

---

### **Child Deep-Dive (Individual Feed Review)**
A granular look at a specific child’s nutritional journey and daily rhythms.
* **Chronological Feed Stream:** Comprehensive logs featuring precise timestamps, milk type (breast/bottle), and volume.
* **Distribution of feed volume over time:** Violin plots comparing variation in individual feed volumes.
* **Anomaly Detection:** Highlights significant deviations from the child’s "normal" feeding amounts.

---

### **Circadian Analytics (Day vs. Night)**
Advanced "Sleep-Aware" metrics that distinguish between active daytime feeding and overnight maintenance.
* **Night vs day feed:** Visual breakdown of calories consumed during night vs day by week per child


## 💾 Data Export

The pipeline can export processed feeding data to Excel files for record-keeping or external analysis.

### Export Options

Exporting is handled by the `DataPipeline.export_data()` method:

```python
pipeline.export_data(
    output_file_name="child_feeding_schedule.xlsx",
    export_errors=True,      # Include rows that failed validation 
    export_validated=True    # Include successfully validated records
)
```

### Export Contents
- **Validated Data**: Cleaned and transformed feeding records that passed all validations
- **Error Records**: Any rows from the raw data that failed validation, along with simple-to-read error messages
- **Summary Sheets**: Daily and weekly aggregated statistics

Exported files are saved to the `reporting/` folder.

## 🛠️ Requirements

To run this project, you will need the following environment and dependencies:

### 🐍 Python Environment
* **Python 3.14+**: This project utilizes the latest Python features and optimizations.
* **uv**: It is highly recommended to use [uv](https://github.com/astral-sh/uv) for dependency synchronization and virtual environment management.

### 📦 Key Dependencies
| Dependency | Version | Purpose |
| :--- | :--- | :--- |
| **Pydantic** | `>=2.12.5` | Data validation and settings management using Python type hints. |
| **Dash** | `>=3.3.0` | Framework for building the analytical web dashboard. |
| **Plotly** | `>=6.5.0` | Interactive data visualizations. |
| **Pandas** | `>=2.3.3` | High-performance data manipulation and transformation. |
| **Statsmodels** | `>=0.14.6` | Statistical analysis tools for feeding patterns. |
| **Pytest** | `>=9.0.2` | Testing framework for validating the ETL pipeline logic. |
| **Dash bootstrap components** | `>=2.0.4` |  Bootstrap components for Plotly Dash to improve styling |

 
## 🧪 Running Tests

Run all unit tests using:

```bash
# Using uv
uv run pytest

# Or using Python directly (if venv is activated)
python -m pytest
```

## 📜 License

Distributed under the **MIT License**. See [LICENSE.txt](LICENSE.txt) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue to discuss proposed changes.
