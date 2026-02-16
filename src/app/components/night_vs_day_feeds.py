'''
Render the nigth vs day feed tab for the Child Feeding Progress Tracker dashboard.
'''

from io import StringIO
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from app.base_graphs import night_vs_day_feed_volume
from app.dashboard_logic import create_page_header


def render_night_vs_day_feeding(
        weekly_df: pd.DataFrame,
        child_options: list[str],
        default_child: str = None)  -> dbc.Container:

    '''
    Render a dashboard component displaying night versus day feeding analysis.
    This function creates a Bootstrap container with a card-based layout that visualizes
    the volume of milk consumed by a child during night versus day feeding periods.
    The component includes a header section with the dashboard title and version info,
    along with an interactive chart that allows users to select different children
    to view their feeding data.
    
    Parameters:
        weekly_df: pd.DataFrame
            DataFrame containing weekly aggregated feeding data, used to generate
            the initial Plotly figure object to display in the night vs day feed volume chart.
        child_options : list[str]
            A list of child names/identifiers to display in the radio button selector.
        default_child : str
            The default child to display in the chart on initial load.

    Returns:
        dbc.Container
            A Bootstrap container component containing:
            - A header row with the dashboard title and version information
            - A card with child selector radio buttons and an interactive graph
            showing the distribution of milk volumes consumed at night versus day
    
    Notes:
        - The component uses Dash Bootstrap Components for responsive layout
        - The chart has a fixed height of 350px and does not display the Plotly mode bar
        - The child selector uses inline radio items for compact horizontal display
    
    '''

    # if no default child, include all children
    if default_child is None:
        default_child = child_options[0]

    initial_fig = night_vs_day_feed_volume(weekly_df)

    return dbc.Container([

            # Header Section
            create_page_header('Volume of Feed Consumed at Night versus Day over time',
            "Where a feed is considered a 'night feed' "
            "if taken between 10.30pm and 6.30am",
            'Feeding data dashboard v1.0',
            'moon-fill'),

            # Individual Feed Volume Distribution Chart
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5('Volume of milk consumed at night versus day',
                                    className='card-title text-nowrap text-truncate'),
                            html.Div([
                                html.Span('Choose child: ', className='fw-bold text-primary me-3'),
                                dbc.RadioItems(
                                    options=child_options,
                                    value=default_child,
                                    id='radioitems-inline-input',
                                    inline=True,
                                ),
                            # align vertically with 'd-flex' in a row
                            ], className='d-flex align-items-center mb-1'),
                            dcc.Graph(id='night-vs-day-feed-volume',
                                        figure=initial_fig,
                                        config={'displayModeBar': False},
                                        style={'height': '350px'},
                                        )
                                      ])
                    ], className='shadow mb-4')
                ], lg=12, md=12)
            ]) # Close Row
            ], fluid=True)

@callback(
    Output('night-vs-day-feed-volume', 'figure'),
    [Input('radioitems-inline-input', 'value'),
     Input('stored-weekly-data', 'data'),
     ]
)
def update_night_day_chart(radio_child_selection, stored_weekly_data):

    '''Input callback to update night vs day feed volume chart based on selected child.'''
    # Convert stored JSON data back to DataFrame
    weekly_df = pd.read_json(StringIO(stored_weekly_data), orient='records')
    weekly_filtered_df = weekly_df.loc[weekly_df['name'] == radio_child_selection]
    return night_vs_day_feed_volume(weekly_filtered_df)
