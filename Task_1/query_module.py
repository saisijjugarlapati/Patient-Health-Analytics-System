import os
import pandas as pd
from statistics_module import StatisticsModule
from load_dataset_module import BaseModule

class QueryError(Exception):
    #Custom exception for query failures
    pass

class QueryModule(BaseModule):
    #Handles all dataset queries and analysis functions.

    def __init__(self, dataframe):
        super().__init__("QueryModule")
        if dataframe is None:
            raise QueryError("DataFrame cannot be None")
        self.__df = dataframe.copy()
        self.__stats = StatisticsModule()   
    
    # Controlled access
    def get_dataframe(self):
        #Returns a safe copy of the internal DataFrame.
        if self.__df is None:
            raise QueryError("No DataFrame available.")
        return self.__df.copy()

    # i) Age stats for smokers with hypertension
    def get_smoking_hypertension_age_stats(self):
        try:
            filtered = self.__df[
                (self.__df["Smoking Status"].isin(["Smokes", "Formerly smoked"])) &
                (self.__df["Hypertension"] == 1)
            ]
            if filtered.empty:
                self.log("No patients found for smoking + hypertension filter.")
                return pd.DataFrame()
            return pd.DataFrame([{
                "mean_age": self.__stats.mean(filtered["Age"]),
                "median_age": self.__stats.median(filtered["Age"]),
                "mode_age": self.__stats.mode(filtered["Age"])
            }])
        except Exception as e:
            raise QueryError(f"Error in smoking hypertension stats: {e}")
        
    # ii) Age stats and average glucose for patients with heart disease
    def get_heart_disease_stats(self):
        try:
            filtered = self.__df[self.__df["Heart Disease"] == 1]
            if filtered.empty:
                self.log("No heart disease patients found.")
                return pd.DataFrame()
            return pd.DataFrame([{
                "mean_age": self.__stats.mean(filtered["Age"]),
                "median_age": self.__stats.median(filtered["Age"]),
                "mode_age": self.__stats.mode(filtered["Age"]),
                "avg_glucose": self.__stats.mean(filtered["Average Glucose Level"])
            }])
        except Exception as e:
            raise QueryError(f"Error in heart disease stats: {e}")
    
    # iii) Compare age stats by gender for hypertension patients with/without stroke
    def get_hypertension_stroke_age_by_gender(self):
        try:
            df_filtered = self.__df[self.__df["Hypertension"] == 1]
            if df_filtered.empty:
                self.log("No hypertension patients found.")
                return pd.DataFrame()
            grouped = (
                df_filtered
                .groupby(["Gender", "Stroke Occurrence"], observed=True)["Age"]
                .agg(mean=self.__stats.mean, median=self.__stats.median, mode=self.__stats.mode)
                .reset_index()
            )
            return grouped
        except Exception as e:
            raise QueryError(f"Error in hypertension stroke gender stats: {e}")
    
    # iv) Average BMI, glucose, and risk score by physical activity level
    def get_stats_by_activity_level(self):
        try:
            return self.__df.groupby("Physical Activity", observed=True).agg({
                "BMI": "mean",
                "Average Glucose Level": "mean",
                "Stroke Risk Score": "mean"
            }).rename(columns={
                "BMI": "avg_bmi",
                "Average Glucose Level": "avg_glucose",
                "Stroke Risk Score": "avg_risk_score"
            })
        except Exception as e:
            raise QueryError(f"Error in activity level stats: {e}")
        
    # v) Age stats for stroke patients in urban vs rural areas
    def get_stroke_age_by_residence(self):
        try:
            filtered = self.__df[self.__df["Stroke Occurrence"] == 1]
            if filtered.empty:
                self.log("No stroke patients found.")
                return pd.DataFrame()
            return filtered.groupby("Residence Type", observed=True)["Age"].agg(
                mean="mean",
                median="median",
                mode=lambda x: x.mode().iloc[0] if not x.mode().empty else None
            ).reset_index()
        except Exception as e:
            raise QueryError(f"Error in stroke residence stats: {e}")
        
    # vi) Count dietary habits for stroke vs non-stroke patients
    def get_dietary_habits_by_stroke(self):
        try:
            return (
                self.__df
                .dropna(subset=["Stroke Occurrence", "Dietary Habits"])
                .groupby("Stroke Occurrence", observed=True)["Dietary Habits"]
                .value_counts()
                .rename("Count")
                .reset_index()
            )
        except Exception as e:
            raise QueryError(f"Error in dietary habits query: {e}")

    # vii) Returns patients with hypertension who had a stroke
    def get_hypertension_stroke_patients(self):
        try:
            result = self.__df[
                (self.__df["Hypertension"] == 1) &
                (self.__df["Stroke Occurrence"] == 1)
            ].reset_index(drop=True)
            self.log(f"Found {len(result)} hypertension stroke patients.")
            return result
        except Exception as e:
            raise QueryError(f"Error retrieving hypertension stroke patients: {e}")
        
    # viii) Get patients with heart disease who had a stroke
    def get_heart_disease_stroke_patients(self):
        try:
            result = self.__df[
                (self.__df["Heart Disease"] == 1) &
                (self.__df["Stroke Occurrence"] == 1)
            ].reset_index(drop=True)
            self.log(f"Found {len(result)} heart disease stroke patients.")
            return result
        except Exception as e:
            raise QueryError(f"Error retrieving heart disease stroke patients: {e}")
        
    # ix) Calculate average sleep hours between stroke vs non-stroke patients
    def get_sleep_hours_by_stroke(self):
        try:
            grouped = self.__df.groupby("Stroke Occurrence", observed=True)["Sleep Hours"]
            return pd.DataFrame([{
                "no_stroke_avg_sleep": self.__stats.mean(grouped.get_group(0)) if 0 in grouped.groups else None,
                "stroke_avg_sleep": self.__stats.mean(grouped.get_group(1)) if 1 in grouped.groups else None
            }])
        except Exception as e:
            raise QueryError(f"Error in sleep hours query: {e}")
        
    # x) Filter patients based on any combination of column criteria.
    def filter_patients(self, **kwargs):
        try:
            df_filtered = self.__df.copy()
            for key, value in kwargs.items():
                if key not in df_filtered.columns:
                    self.log(f"Warning: Column '{key}' not found, skipping filter.")
                    continue
                df_filtered = df_filtered[df_filtered[key] == value]
            return df_filtered.reset_index(drop=True)
        except Exception as e:
            raise QueryError(f"Error filtering patients: {e}")
        
    # xi) Group patients into risk levels and calculate count and percentage
    def categorize_by_risk_group(self):
        try:
            bins = [0, 33, 66, 100]
            labels = ["Low", "Medium", "High"]
            risk = pd.cut(
                self.__df["Stroke Risk Score"],
                bins=bins, labels=labels, include_lowest=True
            )
            counts = risk.value_counts().reindex(labels, fill_value=0)
            percentages = counts / counts.sum() * 100
            return pd.DataFrame({
                "Risk Category": labels,
                "count": counts.values,
                "percentage": percentages.values
            })
        except Exception as e:
            raise QueryError(f"Error categorising risk groups: {e}")
        
    # xii) Summary stats (age, BMI, glucose level, stroke rate) by region
    def generate_regional_summary(self):
        try:
            results = []
            for region, group in self.__df.groupby("Region", observed=True):
                results.append({
                    "Region": region,
                    "Average Age": self.__stats.mean(group["Age"]),
                    "Average BMI": self.__stats.mean(group["BMI"]),
                    "Average Glucose Level": self.__stats.mean(group["Average Glucose Level"]),
                    "Stroke Occurrence Rate": self.__stats.mean(group["Stroke Occurrence"])
                })
            return pd.DataFrame(results)
        except Exception as e:
            raise QueryError(f"Error generating regional summary: {e}")
    
    #Saves query output to CSV file
    def save_output(self, data, filename):
        try:
            output_dir = "test_query_output"
            os.makedirs(output_dir, exist_ok=True)
            path = os.path.join(output_dir, filename)

            if isinstance(data, pd.DataFrame):
                data.reset_index(drop=True).to_csv(path, index=False)
            elif isinstance(data, pd.Series):
                data.reset_index(drop=True).to_frame().to_csv(path, index=False)
            elif isinstance(data, dict):
                pd.json_normalize(data).to_csv(path, index=False)
            else:
                pd.DataFrame([{"value": data}]).to_csv(path, index=False)

            self.log(f"Output saved to {path}")
        except Exception as e:
            raise QueryError(f"Error saving output: {e}")