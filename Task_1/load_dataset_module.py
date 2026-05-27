import pandas as pd
import os

class DataLoadError(Exception):
    #Custom exception for dataset loading failures
    pass

class BaseModule:
    #Base class for all modules
    def __init__(self, module_name):
        self.module_name = module_name

    def log(self, message):
        print(f"[{self.module_name}] {message}")

    def error(self, message):
        print(f"[{self.module_name} ERROR] {message}")

class DataLoader(BaseModule):
#Loads and parses the patient dataset using pandas
    
    def __init__(self, filepath):
        super().__init__("DataLoader")
        self.filepath = filepath 

        #List of dictionaries    
        self.__patient_data = []   # ← private (double underscore) 
        #Assigned after loading data as a DataFrame
        self.__dataframe = None    # ← private 

    def load(self):
        try:
            # Load dataset
            self.__dataframe = pd.read_csv(self.filepath)

            # Categorical columns
            binary_cols = [
                "Hypertension", "Heart Disease", "Ever Married",
                "Alcohol Consumption", "Chronic Stress",
                "Family History of Stroke", "Stroke Occurrence"
            ]

            categorical_cols = [
                "Gender", "Work Type", "Residence Type",
                "Education Level", "Income Level", "Region",
                "Smoking Status", "Physical Activity", "Dietary Habits"
            ]

            # Combine all categorical-type columns
            all_cat_cols = binary_cols + categorical_cols

            # Convert safely with error handling
            for col in all_cat_cols:
                if col in self.__dataframe.columns:
                    try:
                        self.__dataframe[col] = self.__dataframe[col].astype("category")
                    except Exception as e:
                        self.error(f"Could not convert column '{col}' to category. Reason: {e}")
                else:
                    self.log(f"Warning: Column '{col}' not found in dataset.")
            
            #  Convert to list of dictionaries
            self.__patient_data = self.__dataframe.to_dict(orient="records")

            self.log(f"Successfully loaded {len(self.__dataframe)} patient records.")
            self.log(f"Columns found: {list(self.__dataframe.columns)}")
            
            return True

        except FileNotFoundError:
            self.error(f"Could not find file at {self.filepath}")
            raise DataLoadError(f"File not found: {self.filepath}")
        except pd.errors.EmptyDataError:
            self.error("The file is empty.")
            raise DataLoadError("Empty CSV file.")
        except pd.errors.ParserError:
            self.error("Failed to parse CSV file.")
            raise DataLoadError("CSV parse error.")
        except Exception as e:
            self.error(f"Unexpected error: {e}")
            raise DataLoadError(str(e))

    def get_data(self):
        #Returns patient records securely as a list of dictionaries.
        if not self.__patient_data:
            raise DataLoadError("No data loaded. Call load() first.")
        return self.__patient_data
    
    def get_dataframe(self):
        #Returns the loaded dataset as a pandas DataFrame.
        if self.__dataframe is None:
            raise DataLoadError("No data loaded. Call load() first.")
        return self.__dataframe
        
    def get_column_values(self, column_name):
        #Returns all values from a single column as a list (case-insensitive match)
        if self.dataframe is None:
            raise ValueError("No data loaded yet. Run load() first.")

        #Case-insensitive column map
        col_map = {col.lower(): col for col in self.__dataframe.columns}
        
        actual_col = col_map.get(column_name.lower())
        if actual_col is None:
            raise KeyError(
                f"Column '{column_name}' not found. "
                f"Available columns: {list(self.__dataframe.columns)}"
            )

        # Convert to list efficiently
        return self.__dataframe[actual_col].tolist()
         
    def get_summary(self):
        #Prints a quick summary of the dataset
        if self.__dataframe is not None:
            print("\n--Dataset Summary--")
            print(f"Total patients: {len(self.__dataframe)}")
            print(f"Total columns: {len(self.__dataframe.columns)}")
            
            print("\nColumn data types:")
            print(self.__dataframe.dtypes)
            
            print("\nMissing values per column:")
            print(self.__dataframe.isnull().sum())
        else:
            print("No data loaded yet. Run load() first.")

