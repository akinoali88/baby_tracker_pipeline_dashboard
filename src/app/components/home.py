'''
Render the home tab for the Child Feeding Progress Tracker dashboard.
'''

from io import StringIO

from dash import dcc, html, callback, Input, Output
from dash.exceptions import PreventUpdate
import pandas as pd
import dash_bootstrap_components as dbc
from app.dashboard_logic import (
    create_stat_card,
    get_daily_feed_metrics,
    create_page_header,
    create_child_checklist,
    create_age_range_slider
    )
from app.base_graphs import daily_feed_vol_by_age

def render_home_tab(daily_df: pd.DataFrame,
                    slider_parameters: dict,
                    child_options: list[str]) -> dbc.Container:

    '''
    This function constructs the main dashboard layout for tracking infant feeding progress,
    including header information, key statistics, and an interactive chart for visualizing
    daily feed volume over time with age-based filtering.

    Parameters:
        daily_df: pd.DataFram
            DataFrame containing daily feeding data used to generate the
            initial Plotly figure object to display in the daily feed volume chart.
        slider_parameters: dict
            dictionary of:
                min_val : int
                    Minimum value for the age range slider in weeks.
                max_val : int
                    Maximum value for the age range slider in weeks.
                marks : dict
                    Dictionary defining marked positions on the age range slider.
                lowest_max_age : int
                    The lowest maximum age value to set as initial slider endpoint in weeks.
        child_opions: list[str]
            A list of child names available for selection in the feeding tracker.

    Returns:
        dbc.Container
            A Bootstrap container component containing the complete home tab layout with:
            - Header section with title and version information
            - Three statistics cards (total volume, average feed size, feeding days)
            - Interactive range slider for age filtering
            - Daily feed volume chart with dynamic updates based on slider selection
    
    Notes:
        The component uses Dash Bootstrap Components for responsive layout and
        styling. Chart interactions and statistics updates are handled via Dash callbacks
        using the component IDs defined in this function.

    '''

    initial_fig = daily_feed_vol_by_age(daily_df)

    # Get slider parameters
    min_val = slider_parameters['slider']['min']
    max_val = slider_parameters['slider']['max']
    marks = slider_parameters['slider']['marks']
    lowest_max_age = slider_parameters['slider']['lowest_max_age']


    return dbc.Container([
            # Header Section

            create_page_header('Child Feeding Progress Tracker',
                               'Total daily feeding volumes and statistics',
                               'Feeding data dashboard v1.0',
                               icon_class='calendar-check'),

            # Stats Summary Row
            dbc.Row([
                create_stat_card('Total Volume Tracked', 'total-vol-stat', 'primary'),
                create_stat_card('Average Daily Feed Size', 'avg-feed-stat', 'success'),
                create_stat_card('Feeding Days Recorded', 'feed-days-stat', 'info'),
                    ], className='mb-3'),

            # Daily Feed Volume Slider and Chart
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5('Daily Feed Volume Over Time',
                                    className='card-title'),

                            # select child / children
                            create_child_checklist('home', child_options),

                            # Select age range
                            create_age_range_slider('home',
                                                    min_val,
                                                    max_val,
                                                    marks,
                                                    lowest_max_age),

                            # Output graph
                            dcc.Graph(id='daily-feed-volume',
                                      figure=initial_fig,
                                      config={'displayModeBar': False},
                                      style={'height': '350px', 'marginTop': '-20px'},)
                        ])
                    ], className='shadow-sm mb-4')
                ], width=12)
            ]) # Close Row
        ], fluid=True) # Close Container

# Callbacks for home page tab
@callback(
    [Output('daily-feed-volume', 'figure'),
    Output('total-vol-stat', 'children'),
    Output('avg-feed-stat', 'children'),
    Output('feed-days-stat', 'children')],
    [Input('range-slider-home', 'value'),
     Input('child-selection-home','value'),
     Input('stored-daily-data', 'data')]
)
def update_daily_metrics(slider_range, child_selection, stored_daily_data):
    '''Input callback to update daily feed volume figure and
    stats cards based on age range slider.'''

    # no update to charts if no child selected
    if not child_selection:
        raise PreventUpdate

    # Convert stored JSON data back to DataFrame
    daily_df = pd.read_json(StringIO(stored_daily_data), orient='records')

    return get_daily_feed_metrics(slider_range, child_selection, daily_df)
