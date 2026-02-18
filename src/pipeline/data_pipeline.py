''' Module for processing data files including loading, cleaning, and validating.
Steps orchestrated within the DataProcessor class.
'''

from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
from pydantic import ValidationError

from models.children import FeedingData
from models.children import settings

class DataPipeline:
    '''
    Class for loading, cleaning, validating and processing data.
    '''

    # 1. DEFINE CONSTANTS AS CLASS ATTRIBUTES
    # Define ANSI codes for bold and reset
    bold = '\033[1m'
    end_bold = '\033[0m'

    def __init__(self,
                 name: str,
                 file_name: str,
                 dob: datetime,
                 input_dir_path: str = 'data/live data',
                 excel_params: dict = None,
                 use_dummy_data: bool = True):

        '''
        Initializes the DataProcessor with configuration.
        '''

        self.name = name
        self.file_name = file_name
        self.dob = pd.Timestamp(dob)
        self.input_dir_path = input_dir_path
        self.dummy_data = use_dummy_data

        # Initialize blank dataframes to be updated during processing
        self.raw_data: pd.DataFrame = None
        self.daily_data: pd.DataFrame = None
        self.weekly_data: pd.DataFrame = None
        self.validated_data : pd.DataFrame = None
        self.transformed_data : pd.DataFrame = None
        self.input_data_errors: pd.DataFrame = None

        # Define default excel parameters if none are provided
        self.excel_params = excel_params if excel_params is not None else {
            'parse_dates': ['Start', 'Finish']}

        # Calculate and store the absolute file path once
        # Using Path.cwd() assumes 'input_dir_path' is relative to the script's execution location.
        self.full_file_path = Path.cwd() / input_dir_path / file_name

    def __str__(self):

        print_output = (f"DataPipeline(name={self.name}, dob={self.dob.date()})"
                        f"\n validated data {self.validated_data.head()
                            if self.validated_data is not None else 'None'}")

        return print_output

    def _load_data(self) -> pd.DataFrame:

        '''
        Loads the data based on file extension and configured parameters.
        '''

        # Use the stored path attribute
        if not self.full_file_path.exists():

            # If dummy data is enabled, load dummy data instead of raising an error
            if self.dummy_data:

                try:
                    self.file_name = settings.get_file_by_name(self.name)
                except ValueError as e:
                    print(e)

                print(f"\n⚠️ File not found at {self.full_file_path}. "
                    "Loading dummy data instead for development purposes.")

                self.full_file_path = Path.cwd() / 'data/dummy data' / self.file_name

            else:
                raise FileNotFoundError(f"File not found at {self.full_file_path}")

        # Determine the file type
        suffix = self.full_file_path.suffix.lower()

        if suffix in ('.xls', '.xlsx'):
            df = pd.read_excel(self.full_file_path, **self.excel_params)
        elif suffix == '.csv':
            # Example for CSV
            df = pd.read_csv(self.full_file_path, **self.excel_params)
        else:
            raise ValueError(f"Unsupported file type: {suffix} at {self.full_file_path}")

        self.raw_data = df

        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Cleans the data by handling missing values and duplicates.
        Removes non-feeding columns
        Renames columns for clarity and next steps
        '''

        # Run throuhgh cleaning steps

        # Drop rows with missing values and remove unnecessary columns
        df = df.drop_duplicates().drop(columns='Finish')

        # Rename columns and ensure camel case
        df.columns = df.columns.str.lower()
        df = df.rename(columns = {'details' : 'feed_volume_ml',
                                  'start' : 'feed_start_time'})

        # Extract feed volumes
        df['feed_volume_ml'] = df['feed_volume_ml'].str.extract(r'(\d+)').fillna('0')

        # Convert feed volumes to int
        df.feed_volume_ml = df.feed_volume_ml.astype(int)

        return df

    def _validate_inputs(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Validates the data using Pydantic models based model 
        defined in models/children.py.
        Removes invalid records and logs errors.
        '''

        # Access the class constants using self.BOLD and self.END
        bold = self.bold
        end_bold = self.end_bold

        feeding_list = []
        error_records = []

        # Validate each row using Pydantic models
        for record_dict in df.to_dict('records'):
            try:
                # The Pydantic model validates the row data during instantiation
                feed_record = FeedingData(**record_dict)

                # ensures enum values serialized to str by using json mode
                feeding_list.append(feed_record.model_dump(mode='json'))

            except ValidationError as e:

                # Format the message for a single error, separated by new lines
                details = "\n".join(
                    f"{i}) {err['loc'][0]}: {err['msg']}"
                    for i, err in enumerate(e.errors(), 1)
                    )

                # 2. Add one single entry to the error list
                error_records.append({
                    **record_dict,
                    'total_errors': e.error_count(),
                    'error_details': details
                })

        # Create DataFrame for valid records
        idx = pd.to_datetime([r['feed_start_time'] for r in feeding_list])
        df_validated = pd.DataFrame(feeding_list, index=idx)
        df_validated.index.name = 'feed_start_time'
        df_validated = df_validated.drop(columns=['feed_start_time'], errors='ignore')

        # Create DataFrame for error records
        error_df = pd.DataFrame(error_records)

        # --- Summary Report at the End ---
        total_errors = 0
        if 'total_errors' in error_df.columns:
            total_errors = error_df['total_errors'].sum()

        if total_errors > 0:

            input_label = "input has" if total_errors == 1 else "inputs have"

            print(f"✅ {len(df_validated)} / {len(df)} records have passed validation checks. "
                  f"\n🚨 {total_errors} {input_label} failed validation for "
                  f"{bold}{self.name}{end_bold} datasets. "
                  "Please investigate further.")

        else:
            print("\n✅ All rows passed validation successfully for "
                  f"{bold}{self.name}{end_bold} datasets.")

        self.input_data_errors = error_df
        self.validated_data = df_validated

        return df_validated

    def _transform_data(self, df: pd.DataFrame) -> pd.DataFrame:

        '''
        Completes transformation steps for baby feeding data.
        
        Adds baby name and age information to the input dataframe, calculates
        daily feeding statistics, and generates aggregated daily feeding data.
        
        Effects:
            Sets self.transformed_data with the enriched input dataframe.
            Sets self.daily_data with aggregated daily feeding statistics including:
                - name: Baby's name
                - age_in_days: Age in days
                - age_in_weeks: Age in weeks
                - daily_feed_volume_ml: Total feed volume per day
                - feeds_per_day: Number of feeding sessions per day
                - average_intake_per_feed: Average volume per feeding session
                - age_in_months: Age in months (calculated using avg_days_in_month)
                - night vs day feed classification 
        
        Note:
            The last day of data is removed from daily_data as it may be incomplete.
        '''

        # Run through tranform steps

        # Add name to dataframe
        df['name'] = self.name

        # Expand timing classifications to dataframe
        age = df.index - self.dob
        df['age_in_weeks'] = (age.days // 7).astype(int)
        df['age_in_days'] = age.days.astype(int)
        df['time'] = df.index.time

        # Define feed as day vs night:
        # Night Feed: 00:00 - 06:59 and 23:00 - 23:59

        # Create a fractional hour (e.g., 10:30 -> 22.5)
        hours = df['time'].apply(lambda x: x.hour + x.minute / 60)

        # Create a formatted string version of the time for the tooltip
        df['time_str'] = df.index.strftime('%I:%M %p')

        # Night is after 22.5 (10:30 PM) or before 6.5 (6:30 AM)
        df['night_or_day'] = np.where((hours >= 22.5) | (hours < 6.5), 'Night', 'Day')

        self.transformed_data = df

        # Create Dataframe to represent daily feeding data
        daily_fd = df.resample('D').agg(
            name = ('name', 'first'),
            age_in_days = ('age_in_days', 'first'),
            age_in_weeks = ('age_in_weeks', 'first'),
            daily_feed_volume_ml = ('feed_volume_ml', 'sum'),
            feeds_per_day = ('feed_volume_ml', 'count'),
            average_intake_per_feed = ('feed_volume_ml', 'mean'))

        #remove last day - by definition this will not be complete
        daily_fd = daily_fd.drop(daily_fd.tail(1).index)

        # Divide the total days by the average number of days in a month.
        avg_days_in_month = 30.4375

        daily_fd['age_in_months'] = daily_fd['age_in_days'] /  avg_days_in_month

        daily_fd = daily_fd.sort_values(by='age_in_days')

        # Create weekly dataframe to support night vs day analysis

        weekly_df = df.groupby(['age_in_weeks', 'night_or_day']).agg(
            name = ('name', 'first'),
            total_feed_volume_ml = ('feed_volume_ml', 'sum'),
            feeds_count = ('feed_volume_ml', 'count')).reset_index()

        # Calculate weekly totals to get percentage total
        weekly_totals = weekly_df.groupby('age_in_weeks')['total_feed_volume_ml'].transform('sum')

        # Create the custom text label for night vs day plot
        weekly_df['text_label'] = ([f"{vol:,.0f}mL<br>({(vol/tot)*100:.0f}%)"
            for vol, tot in zip(weekly_df['total_feed_volume_ml'], weekly_totals)])

        self.daily_data = daily_fd
        self.weekly_data = weekly_df

        return df

    def process(self) -> pd.DataFrame:
        '''
        Orchestrates loading, cleaning and validation processes.
        '''

        raw_data = self._load_data()
        cleaned_data = self._clean_data(raw_data)
        validated_data = self._validate_inputs(cleaned_data)
        self._transform_data(validated_data)
        return

    def export_data(self,
                        output_file_name: str,
                        export_errors: bool = False,
                        export_validated: bool = False,
                        output_folder: str = 'reporting') -> None:
        '''
        Exports the selected internal data (errors and/or validated data) 
        to an Excel file, creating a separate sheet for each type.

        Args:
            output_file_name: The name of the output Excel file (e.g., 'data_report.xlsx').
            export_errors: If True, exports self.input_data_errors to 'Input Data Errors' sheet.
            export_validated: If True, exports self.validated_data to 'Validated Data' sheet.
            output_folder: The sub-folder relative to the current working directory.
                            Defaults to 'reporting'.
        '''

        # Prepare data mapping and checks
        data_to_export = []

        input_errors_exist = (
            export_errors and
            hasattr(self, 'input_data_errors') and
            self.input_data_errors is not None and
            not self.input_data_errors.empty
        )

        if input_errors_exist:
            data_to_export.append({
                'df': self.input_data_errors,
                'sheet_name': 'Input Data Errors',
                'description': 'Input Data Errors'
            })

        validated_data_exist = (
            export_validated and
            hasattr(self, 'validated_data') and
            self.validated_data is not None and
            not self.validated_data.empty)

        if validated_data_exist:
            data_to_export.append({
                'df': self.validated_data,
                'sheet_name': 'Validated Data',
                'description': 'Validated Data'
            })

        # Early exit if no data is selected or available
        if not data_to_export:
            if not export_errors and not export_validated:
                print("\n⚠️ No data selected for export. "
                    "Set 'export_errors' or 'export_validated' to True.")
            else:
                # If selected, but the data attribute was None/Empty
                print("\n✅ No available data to export for the selected options.")
            return

        # Convert output_folder string to a Path object relative to CWD
        output_dir = Path.cwd() / output_folder

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"\n❌ Permission Denied: Cannot create folder at {output_dir}."
                  "Check access rights.")
            return
        except OSError as e:
            print(f"\n❌ General OS Error creating directory '{output_dir}': {e}")
            return

        output_file = output_dir / output_file_name # Final output path

        # Perform the multi-sheet export with robust error handling
        try:
            with pd.ExcelWriter(output_file, datetime_format='dd/mm/yyyy') as writer:
                exported_items = []
                for item in data_to_export:
                    item['df'].to_excel(writer,
                                        sheet_name=item['sheet_name'],
                                        index=False)
                    exported_items.append(item['description'])

            # Success message generation
            bold = self.bold
            end_bold = self.end_bold

            exported_list_str = " and ".join(exported_items)

            print(f"\n✅ Export successful for {bold}{self.name}{end_bold}:")
            print(f"   {exported_list_str} exported to **{output_file_name}**.")
            print(f"   Location: {output_file.relative_to(Path.cwd())}")

        except PermissionError:
            print(f"\n❌ Permission Denied: The file {output_file.name} is likely **open**."
                "Please close it and retry.")
            return
        except (OSError, IOError) as e:
            print(f"\n❌ Failed to export data to {output_file}: {e}")
            return
