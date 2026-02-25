'''
Baby Feeding Schedules Main Application Module

This module serves as the entry point for the Baby Feeding Schedules application.
It orchestrates the data processing pipeline for multiple children,
and creates an interactive Dash dashboard for visualization.

Workflow:
1. Initializes DataPipeline objects for each child defined in settings
2. Processes raw feeding schedule data for each child
3. Combines data from all children across different time periods (raw, daily, weekly)
4. Instantiate Dash web application with interactive charts and visualizations

Dependencies:
    - pandas: Data manipulation and concatenation
    - src.pipeline.data_pipeline: DataPipeline class for data processing
    - src.app.app_factory: Dash app creation factory
    - src.models.children: Child settings and configuration

Global Variables:
    child_pipelines (list): Stores DataPipeline objects for each child
    child_1_data (DataPipeline): Processed pipeline for child 1
    child_2_data (DataPipeline): Processed pipeline for child 2
    combined_data (pd.DataFrame): Concatenated transformed data from all children
    combined_daily_data (pd.DataFrame): Concatenated daily aggregated data from all children
    combined__weekly_data (pd.DataFrame): Concatenated weekly aggregated data from all children
    app (Dash): Dash application instance

Note:
    The application runs on localhost:8051 in debug mode with reloader disabled.
'''

import pandas as pd
from dash import Dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from pipeline.data_pipeline import DataPipeline
from app.app_factory import create_dash_app
from models.children import settings

# Run data pipelines for each child
# hold your processed DataPipeline objects
child_pipelines = []

# Get child settings from .env file and create DataPipeline objects
# If no .env file is found, use default settings defined in models/children.py
for child in settings.children:
    pipeline = DataPipeline(
        name=child.name,
        file_name=child.file_name,
        dob=child.dob
    )
    child_pipelines.append(pipeline)

# Get individual child data pipelines
child_1_data = child_pipelines[0]
child_2_data = child_pipelines[1]

# Run data piepline
child_1_data.process()
child_2_data.process()

# Create charts
combined_data = pd.concat(
    [child_2_data.transformed_data, child_1_data.transformed_data],
    )

combined_daily_data = pd.concat(
    [child_2_data.daily_data, child_1_data.daily_data],
    )

combined__weekly_data = pd.concat(
    [child_2_data.weekly_data, child_1_data.weekly_data],
    )

# load bootstrap figure templates
load_figure_template('minty')
DBC_CSS = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css'

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, DBC_CSS, dbc.icons.BOOTSTRAP])
app.layout = create_dash_app(combined_data, combined_daily_data, combined__weekly_data )

server = app.server

# Create Dash app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=8051)
