'''
Base graph functions for visualizing baby feeding data.
Provides functions to create Plotly figures for daily feed volume by age
and violin plots of feed volume distributions.
'''
import math
import pandas as pd
import plotly.express as px
import numpy as np
from plotly.graph_objects import Figure


def daily_feed_vol_by_age(df: pd.DataFrame) -> Figure:
    '''
    Generate a scatter plot visualizing daily feed volume by age in days.
    This function creates an interactive Plotly scatter plot with a rolling trendline
    to display the relationship between a baby's age and their daily feed volume.
    The plot is colored by child name to support tracking multiple children.
    
    Args:
        df (pd.DataFrame): A DataFrame containing the following columns:
            - age_in_days (int): Age of the child in days
            - daily_feed_volume_ml (float): Daily feed volume in milliliters
            - name (str): Name of the child
            
    Returns:
        Figure: A Plotly Figure object representing the scatter plot with trendlines.
    '''

    fig = px.scatter(df,
                 x='age_in_days',
                 y='daily_feed_volume_ml',
                 color='name',
                 trendline='rolling',
                 trendline_options=dict(window=5),
                 hover_data={
                     'name': False, # Use this as the title instead
                     'age_in_days': True,
                     'daily_feed_volume_ml': True,
                 },
                 labels={
                    'age_in_days': 'Age (days)',
                    'daily_feed_volume_ml': 'Daily Feed Volume (mL)',
                    'name': 'Child'
                 })

    # Calculate where the week marks should be (0, 7, 14, 21...)
    max_days = int(df['age_in_days'].max()) if not df.empty else 70
    week_indices = np.arange(0, max_days + 7, 7)
    # Create the text labels (0, 1, 2, 3...)
    week_labels = [str(i // 7) for i in week_indices]

    fig.update_xaxes(
        title_text='Age (weeks)',    # This changes the axis label without affecting tooltips
        automargin=True,
        rangemode='tozero',
        tickmode='array',
        showline=True,
        tickvals=week_indices,
        ticktext=week_labels,
        )

    fig.update_yaxes(rangemode='tozero')

    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    # Define hover template
    marker_hovertemplate = (
        '<b>%{customdata[0]}</b><br>' +  # 'name' is the first index in customdata
        'Age: %{x} days<br>' +
        'Daily feed volume: %{y} ml<br>'
    )

    trendline_hovertemplate = (
        '<b>%{fullData.name} rolling 5 day average</b><br>' +
        'Age: %{x} days<br>' + 
        'Rolling average 5-day feeding volume: %{y:.0f} ml<br>')

    # Update marker hovertemplate
    fig.update_traces(
        selector=dict(mode='markers'),
        hovertemplate=marker_hovertemplate)

    # Update trendline hovertemplate
    fig.update_traces(
        selector=dict(mode='lines'),
        hovertemplate=trendline_hovertemplate)

    # Add padding to upper y-axis limit for better readability
    padded_peak_volume = df['daily_feed_volume_ml'].max() * 1.35
    y_axis_upper_bound  = math.ceil(padded_peak_volume / 200) * 200
    fig.update_yaxes(range=[0, y_axis_upper_bound], tickformat=',')

    # Add light box around axes
    fig.update_xaxes(showline=True, linewidth=.5, linecolor='lightgrey', mirror=True)
    fig.update_yaxes(showline=True, linewidth=.5, linecolor='lightgrey', mirror=True)

    return fig

def violin_plot_feed_volume(df: pd.DataFrame) -> Figure:
    '''
    Create a violin plot visualization of baby feeding volumes by age.
    This function generates an interactive violin plot showing the distribution of feeding volumes
    across different ages (in weeks) for different babies. The plot includes box plots and all
    individual data points for detailed analysis.

    Args:
        df : pd.DataFrame
            DataFrame containing feeding data with columns:
            - feed_volume_ml : numeric, the volume of feed in milliliters
            - age_in_weeks : numeric, the age of the baby in weeks
            - name : str, the name/identifier of the baby
            - other columns : additional data to display on hover
    Returns
        Figure
            A Plotly Figure object containing the interactive violin plot.
            The plot displays:
            - Y-axis: feed_volume_ml (feeding volume in milliliters) per individual feed
            - X-axis: age_in_weeks (age in weeks)
            - Color: differentiated by baby name
            - Box plot overlaid on violin plot
            - All individual data points displayed
    
    '''


    fig = px.violin(df,
                    y='feed_volume_ml',
                    x='age_in_weeks',
                    color='name',
                    box=True,
                    points='all',
                    title='Distribution of feed volume by week',
                    hover_data=[
                        'name', # Use this as the title instead
                        'age_in_days',
                        'time_str',
                        'type',
                    ],
                    labels={
                        'age_in_weeks': 'Age (weeks)',
                        'feed_volume_ml': 'Feed Volume (mL)',
                        'name': 'Child'
                 })

    hovertemplate = (
        '<b>%{customdata[0]}</b><br>' +  # 'name' is the first index in customdata
        'Age: %{customdata[1]} days<br>' +
        'Feed volume: %{y} ml<br>' +
        'Time: %{customdata[2]}<br>' +
        'Type: %{customdata[3]}<br>'
    )

    # Update the traces to cap the distribution
    fig.update_traces(spanmode='hard', # do not draw curve beyond min/max data points
                      hovertemplate=hovertemplate
                      )

    # Add padding to upper y-axis limit for better readability
    padded_peak_volume = df['feed_volume_ml'].max() * 1.35
    y_axis_upper_bound  = math.ceil(padded_peak_volume / 20) * 20
    fig.update_yaxes(range=[0, y_axis_upper_bound])

    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    # Add light box around axes
    fig.update_xaxes(showline=True, linewidth=.5, linecolor='lightgrey', mirror=True)
    fig.update_yaxes(showline=True, linewidth=.5, linecolor='lightgrey', mirror=True)

    return fig

def night_vs_day_feed_volume(df: pd.DataFrame) -> Figure:

    '''
    Placeholder function for night vs day feed volume visualization.
    This function is intended to create a Plotly figure comparing night and day feeding volumes.
    Currently, it returns an empty figure and should be implemented with actual logic.

    Args:
        df : pd.DataFrame
            DataFrame containing weekly feeding data with name, age_in_weeks,
            total_feed_volume_ml, and night_or_day columns.
    Returns:
        Figure
            A Plotly Figure object of a stacked night vs day feeding volume comparison bar chart

    '''

    fig = px.bar(df,
                 x='age_in_weeks',
                 y='total_feed_volume_ml',
                 color="night_or_day",
                 labels={
                    'age_in_weeks': 'Age (weeks)',
                    'total_feed_volume_ml': 'Weekly Feed Volume (mL)',
                    'night_or_day': 'Feed Time'
                    },
                text='text_label',
                hover_data=['night_or_day','text_label']
                )

    # Update hover template
    hovertemplate = (
        '<b>%{customdata[0]} Feed</b><br>' +  # 'name' is the first index in customdata
        'Age: %{x} weeks<br>' +
        'Feed volume (% of weekly feed): %{customdata[1]}')

    fig.update_traces(hovertemplate=hovertemplate)

    # Updating spacing between chart and header avoce
    fig.update_layout(margin=dict(l=40, r=20, t=10, b=40))

    # Add padding to upper y-axis limit for better readability
    padded_peak_volume = df['total_feed_volume_ml'].max() * 1.5
    y_axis_upper_bound = math.ceil(padded_peak_volume / 2000) * 2000
    fig.update_yaxes(range=[0, y_axis_upper_bound])

    # Add light box around axes
    fig.update_xaxes(showline=True, linewidth=.5, linecolor='lightgrey', mirror=True)
    fig.update_yaxes(showline=True,
                     linewidth=.5, linecolor='lightgrey', mirror=True, tickformat=',')

    return fig
