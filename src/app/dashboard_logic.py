
'''Module for dashboard logic functions including
calculation of feed metrics, stat cards, page headeres
and child checklists

'''

import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
from .base_graphs import daily_feed_vol_by_age


def get_daily_feed_metrics(slider_range: list,
                           child_selection: list,
                           daily_df: pd.DataFrame) -> dict:
    '''
    Calculate key daily feed metrics for the first page of the dataframe, including
    slider ranges, updated figures from the call back and the statistics for the scorecard.
    
    Parameters:
        slider_range : list
            A list containing [low, high] values representing the age range in weeks to filter data.
        child_selection : list
            A list of child names to include in the filtered results.
        daily_df : pd.DataFrame
            The input dataframe containing daily feed data with columns 'age_in_weeks', 'name', 
            and 'daily_feed_volume_ml'.
    Returns:
        - daily_feed_fig : plotly.graph_objects.Figure
            The generated figure showing daily feed volume by age.
        - total_vol : str
            Total feed volume in liters (L) for the filtered data.
        - avg_feed : str
            Average feed volume in milliliters (mL) for the filtered data.
        - total_count : str
            Total count of feed records in the filtered data.
    
    '''

    # Filter data based on slider range
    low, high = slider_range
    mask = ((daily_df['age_in_weeks'] >= low) &
            (daily_df['age_in_weeks'] <= high) &
            (daily_df['name'].isin(child_selection)))
    filtered_df = daily_df[mask]

    # Generate figure
    daily_feed_fig = daily_feed_vol_by_age(filtered_df)

    # Calculate Statistics for scorecard
    total_vol = f"{filtered_df['daily_feed_volume_ml'].sum() / 1000:.1f} L"
    avg_feed = f"{filtered_df['daily_feed_volume_ml'].mean():.0f} mL"
    total_count = f"{len(filtered_df)}"

    return daily_feed_fig, total_vol, avg_feed, total_count



def create_stat_card(title: str,
                     id_name: str,
                     text_color: str ='primary',
                     width: int =4) -> dbc.Col:
    '''
    Returns a Bootstrap Column containing a styled Card for metrics.

    Parameters:
        title : str
            The title text to display at the top of the card.
        id_name : str
            The HTML id attribute for the card's H2 element, used for dynamic content updates.
        text_color : str, optional
            The text color class suffix for Bootstrap styling (default is 'primary').
            Examples: 'primary', 'success', 'danger', 'warning', 'info'
        width : int, optional
            The Bootstrap grid width (1-12) for the column (default is 4).
    Returns:
        dbc.Col
            A Dash Bootstrap Column component containing a Card with centered,
            styled metric display. The card includes a muted title header and
            a large H2 element for the metric value.

    '''
    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.H6(title,
                        className='text-muted mb-0',
                        style={'fontSize': '0.9rem'}),
                html.H2(id=id_name,
                        className=f'text-{text_color} mb-0')
            ], className='py-2')
        ], className='text-center shadow-sm'),
        width=width
    )


def create_page_header(header_title: str,
                       subtitle: str,
                       footer_text: str ='',
                       icon_class: str = None) -> dbc.Card:
    '''
    Creates a standardized, reusable header card for dashboard pages.
    This function generates a header card that includes a main title, a subtitle, 
    and an optional footer text. The card is designed to maintain a consistent 
    appearance across different dashboard pages, enhancing the user interface 
    and user experience.
    
    Parameters:
        header_title : str
            The main title to be displayed prominently at the top of the card.
        subtitle : str
            A brief description or subtitle that provides additional context 
            related to the header title.
        footer_text : str, optional
            An optional text displayed at the bottom of the card. This can be used 
            for additional information or notes. Defaults to an empty string.
        icon_class : str, optional
            The Bootstrap Icon class (e.g., 'bi-droplet-fill').
            If provided, it appears above the footer_text.
    Returns:
        dbc.Card
            A Dash Bootstrap Component Card object containing the formatted header 
            with the specified title, subtitle, and footer text.
        
    '''

    # Prepare the icon element if a class is provided
    # This version handles it whether you pass "droplet" or "bi-droplet"
    icon_element = None

    if icon_class:
        icon_to_display = icon_class.replace('bi-', '')
        icon_element = html.I(
            className=f"bi bi-{icon_to_display} text-primary mb-1",
            style={'fontSize': '2rem'}
    )
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H2(header_title,
                                className='text-primary fw-bold mb-0'),
                        html.P(subtitle,
                                className='text-muted small mb-0 italic'),
                    ], className='ps-3 border-start border-primary border-4')
                ], width=8),

                # Right side: Icon (top) and Footer Text (bottom)
                dbc.Col(
                    html.Div([
                        icon_element,
                        html.Small(footer_text, className='text-muted'),
                    ], className='d-flex flex-column align-items-end'),
                    width=4, className='align-self-center'
                )
            ], className='align-items-center')
        ], className='py-2 px-3')
    ],
    className='shadow-sm border-0 mb-3 mt-3',
    style={'borderRadius': '10px'}
    )


def create_child_checklist(id_suffix: str,
                          options: list,
                          default_value: list = None) -> html.Div:
    '''
    Returns a styled checklist selector for children.
    id_suffix: unique string to distinguish IDs between pages (e.g., 'page1')

    Parameters:
        id_suffix (str): Unique string to distinguish IDs between pages (e.g., 'page1').
            Used to create dynamic component IDs to avoid conflicts.
        options (list): List of dictionaries containing 'label' and
            'value' keys for checklist options. 
            Typically represents available children to select from.
        default_value (list): List of default selected values. If empty or None, no children 
            are pre-selected. Values should match option 'value' fields.
    
    Returns:
        html.Div: A Dash HTML Div component containing a styled label and a checklist 
            component with inline layout and custom styling.

    '''

    # Set all children to default value if no inputs
    if default_value is None:
        default_value = options

    return html.Div([
        html.Span('Select Child:', className='fw-bold text-primary me-3'),
        dcc.Checklist(
            id=f'child-selection-{id_suffix}', # Dynamic ID
            options=options,
            value=default_value if default_value else [],
            inline=True,
            labelStyle={
                'margin-right': '20px', 
                'display': 'inline-block',
                'cursor': 'pointer'
            },
            inputStyle={'margin-right': '8px'}
        ),
    ], className='d-flex align-items-center mb-3')


def create_age_range_slider(id_suffix: str,
                            min_val: int,
                            max_val: int,
                            marks: dict,
                            default_upper: int = None) -> html.Div:
    '''
    Creates a consistent Age Filter RangeSlider component for Dash applications.
    This function generates a styled range slider input with accompanying label text,
    allowing users to filter data by age range in weeks. The slider is wrapped in a
    Div container with Bootstrap margin styling.
    
    Parameters:
        id_suffix : str
            Unique string identifier suffix for the component ID (e.g., 'daily' or 'weekly').
            The full component ID will be formatted as 'range-slider-{id_suffix}'.
        min_val : int
            Minimum value for the range slider.
        max_val : int
            Maximum value for the range slider.
        marks : dict
            Dictionary mapping slider values to their display labels on the slider.
        default_upper : int, optional
            The initial end-point value for the slider range. If not provided, defaults to max_val.

    Returns:
        html.Div
            A Dash HTML Div component containing the RangeSlider with label and description text.
            Includes Bootstrap styling classes for layout and spacing.

    '''
    # Ensure the default value is within range
    upper_value = default_upper if default_upper is not None else max_val

    return html.Div([
        html.P([
            html.Span('Age Filter: ', className='fw-bold text-primary pt-2'),
            'select the age range for the chart below:'
        ]),
        dcc.RangeSlider(
            id=f'range-slider-{id_suffix}',
            # min=min_val,
            # max=max_val,
            marks=marks,
            value=[min_val, upper_value],
            className='dbctext-nowrap',
            allow_direct_input=False

        ),
    ], className='mb-3') # Added margin-bottom for better layout spacing


def get_slider_params(df: pd.DataFrame) -> dict:

    '''
    Generate slider parameters based on age data from a DataFrame.
    This function extracts age statistics from a DataFrame containing baby feeding
    schedule information and returns configuration parameters for a range slider.
    If the DataFrame is empty, returns default slider parameters with no range.
    Args:
        df (pandas.DataFrame): A DataFrame containing at least an 'age_in_weeks' column
                              and a 'name' column for grouping by individual children.
                              Expected to have columns: 'name', 'age_in_weeks'.
    Returns:
        dict: A dictionary containing slider configuration with the following keys:
            min : (int) 
                Minimum value for the slider (always 0)
            max : (int) 
                Maximum age in weeks across all records
            marks : (dict) 
                Dictionary mapping week intervals to label strings,
                generated at 2-week intervals from min to max
            value : (list)
                List of two integers [start, end] representing the
                default selected range, where start is 0 and end is
                the lowest maximum age across individual children
            child_opions: list[str]
                A list of child names available for selection in the feeding tracker.

    '''

    if df.empty:
        return {
            'slider': {'min': 0, 'max': 0, 'marks': {0: '0 wks'}, 'value': [0, 0]},
            'children': {'options': [], 'value': []}
        }

    # 1Slider Parameters
    min_val = 0
    max_val = int(df['age_in_weeks'].max())
    lowest_max_age = int(df.groupby('name')['age_in_weeks'].max().min())
    marks = {t: f'{t} wks' for t in range(min_val, max_val + 1, 2)}

    # 2. Child Selection Parameters
    unique_children = sorted(df['name'].dropna().unique())

    return {
        'slider': {
            'min': min_val,
            'max': max_val,
            'marks': marks,
            'lowest_max_age': lowest_max_age
        },
        'children': {
            'options': [{'label': n, 'value': n} for n in unique_children],
            'value': unique_children  # Set all children as default
        }
    }
