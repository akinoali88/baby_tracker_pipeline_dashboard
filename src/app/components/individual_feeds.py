'''
Render the individual feeds page tab for the Child Feeding Progress Tracker dashboard.
'''

from io import StringIO
from dash import dcc, html, callback, Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
from app.base_graphs import violin_plot_feed_volume
from app.dashboard_logic import (
    create_page_header, create_child_checklist, create_age_range_slider)

def render_individual_feeds_tab(df: pd.DataFrame,
                                slider_parameters: dict,
                                child_options: list[str],
                                ) -> dbc.Container:

    '''
    This function constructs the layout for the individual feeding summary tab,
    including header information, an age range slider, and a violin plot chart
    for visualizing feed volume distributions for a specific child.

    Parameters:
        df: pd.DataFrame
            DataFrame containing aggregated or processed feeding data with 'age_in_weeks' column.
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
            - Interactive range slider for age filtering
            - Individual feed volume distribution chart based on slider selection
    
    Notes:
        The component uses Dash Bootstrap Components for responsive layout and
        styling. Chart interactions and statistics updates are handled via Dash callbacks
        using the component IDs defined in this function.

    '''

    initial_fig = violin_plot_feed_volume(df)

    # Get slider parameters
    min_val = slider_parameters['slider']['min']
    max_val = slider_parameters['slider']['max']
    marks = slider_parameters['slider']['marks']
    lowest_max_age = slider_parameters['slider']['lowest_max_age']

    return dbc.Container([

            # Header Section
            create_page_header('Distribution of Individual Feed Volumes',
                               'Track the distribution of individual feedings.'
                               'Hover over data points for additional details on each entry.',
                               'Feeding data dashboard v1.0',
                               'clipboard-pulse'),

            # Individual Feed Volume Distribution Chart
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5('Individual Feed Volume Over Time',
                                    className='card-title'),

                            # select child / children
                            create_child_checklist('individual',
                                                   child_options),

                            # Select age range
                            create_age_range_slider('individual',
                                                    min_val,
                                                    max_val,
                                                    marks,
                                                    lowest_max_age),

                            # Output graph
                            dcc.Graph(id='avg-feed-volume',
                                        figure=initial_fig,
                                        config={'displayModeBar': False},
                                        style={'height': '350px'})
                        ])
                    ], className='shadow mb-4')
                ], lg=12, md=12)
            ]) # Close Row
            ], fluid=True) # Close Container

@callback(
    Output('avg-feed-volume', 'figure'),
    [Input('range-slider-individual', 'value'),
     Input('child-selection-individual','value'),
     Input('stored-main-data', 'data')]
    )
def update_individual_violin(slider_range, child_selection, stored_main_data):

    '''Input callback to update individual feed volume violin plot based on age range slider.'''

    # no update to charts if no child selected
    if not child_selection:
        raise PreventUpdate

    # Convert stored JSON data back to DataFrame
    df = pd.read_json(StringIO(stored_main_data), orient='records')

    low, high = slider_range
    filtered_df = df[(df['age_in_weeks'] >= low) & (df['age_in_weeks'] <= high) &
            (df['name'].isin(child_selection))]
    return violin_plot_feed_volume(filtered_df)
