import numpy as np
import pandas as pd
from load_dataset_module import BaseModule

class StatisticsError(Exception):
    #Custom exception for statistics computation failures
    pass

class StatisticsModule(BaseModule):
    #Statistical functions for pandas Series, supporting flexible data analysis.
    
    def __init__(self):
        super().__init__("StatisticsModule")

    def _get_numeric_values(self, series):
        #Validates and returns clean numeric values from a pandas Series.
        if not isinstance(series, pd.Series):
            raise StatisticsError("Input must be a pandas Series")
        if series.empty:
            raise StatisticsError("Series is empty")
        values = pd.to_numeric(series, errors="coerce").dropna()
        if values.empty:
            raise StatisticsError("No valid numeric values in Series")
        return values
    
    # -----------------------------
    # Core statistical functions
    # -----------------------------
    def mean(self, series):
        #Returns the mean (average).
        try:
            return np.mean(self._get_numeric_values(series))
        except StatisticsError:
            raise
        except Exception as e:
            raise StatisticsError(f"Error computing mean: {e}")

    def median(self, series):
        #Returns the median (middle value).
        try:
            return np.median(self._get_numeric_values(series))
        except StatisticsError:
            raise
        except Exception as e:
            raise StatisticsError(f"Error computing median: {e}")

    def mode(self, series):
        #Returns the most frequent value for numeric or categorical data.
        try:
            if not isinstance(series, pd.Series):
                raise StatisticsError("Input must be a pandas Series")
            values = series.dropna()
            if values.empty:
                return None
            mode_vals = values.mode()
            return mode_vals.iloc[0] if not mode_vals.empty else None
        except StatisticsError:
            raise
        except Exception as e:
            raise StatisticsError(f"Error computing mode: {e}")

    def variance(self, series):
        #Returns variance.
        try:
            return np.var(self._get_numeric_values(series))
        except StatisticsError:
            raise
        except Exception as e:
            raise StatisticsError(f"Error computing variance: {e}")

    def std_dev(self, series):
        #Returns standard deviation.
        try:
            return np.std(self._get_numeric_values(series))
        except StatisticsError:
            raise
        except Exception as e:
            raise StatisticsError(f"Error computing standard deviation: {e}")

    def minimum(self, series):
        #Returns minimum value.
        try:
            return np.min(self._get_numeric_values(series))
        except StatisticsError:
            raise
        except Exception as e:
            raise StatisticsError(f"Error computing minimum: {e}")

    def maximum(self, series):
        #Returns maximum value.
        try:
            return np.max(self._get_numeric_values(series))
        except StatisticsError:
            raise
        except Exception as e:
            raise StatisticsError(f"Error computing maximum: {e}")

    def data_range(self, series):
        #Returns range (max - min).
        try:
            values = self._get_numeric_values(series)
            return np.max(values) - np.min(values)
        except StatisticsError:
            raise
        except Exception as e:
            raise StatisticsError(f"Error computing range: {e}")

    # -----------------------------
    # Summary statistics
    # -----------------------------
    def describe(self, series, feature_name=""):
        #Returns a dictionary of all summary statistics for a given feature.
        try:
            values = self._get_numeric_values(series)
            desc = values.describe()
            mode_vals = values.mode()
            mode = mode_vals.iloc[0] if not mode_vals.empty else None

            self.log(f"Computed descriptive stats for '{feature_name}'")

            return {
                "feature": feature_name,
                "mean": desc['mean'],
                "median": desc['50%'],
                "mode": mode,
                "std_dev": desc['std'],
                "variance": desc['std'] ** 2,
                "min": desc['min'],
                "max": desc['max'],
                "range": desc['max'] - desc['min']
            }
        except StatisticsError:
            raise
        except Exception as e:
            raise StatisticsError(f"Error computing descriptive statistics: {e}")