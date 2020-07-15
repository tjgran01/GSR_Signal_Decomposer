import pandas as pd
import datetime
import os
import numpy as np
from biosppy.signals import eda

import pickle

import matplotlib.pyplot as plt

class TimestampMatcher(object):
    def __init__(self, shimmer_dir="./shimmer/", log_dir="./logs/",
                 feature_path="./pickled/feature_dicts.pkl",
                 csv_path="./exports/", export=True):
        self.shimmer_dir = shimmer_dir
        self.log_dir = log_dir
        self.csv_path = csv_path

        # Load in files.
        self.file_dict = self.load_shimmer_files()
        self.log_dict = self.load_log_files()

        # Pretty Self Explainatory ... I hope.
        self.place_event_markers(export=export)

        # Checks if the data is already pickled. If not, makes it.
        # If so, loads it.
        if not os.path.exists(feature_path):
            self.scrs = self.extract_scrs(feature_path)
        else:
            self.scrs = pickle.load(open(feature_path, 'rb'))

        # Does canned peak detection for each file.
        for k, v in self.scrs.items():
            print(f"{k}: {len(v['peaks'])} detected")


    def extract_scrs(self, feature_path):

        data = {}
        for k, v in self.file_dict.items():
            if k == "par1_palm":
                rate=1024.0
            else:
                rate=128.0
            eda_features = eda.eda(v["GSR_Skin_Conductance(uS)"].values, sampling_rate=128.0)
            print(type(eda_features))
            data[k] = dict(eda_features)

        pickle.dump(data, open(feature_path, 'wb'))
        return data


    def create_dict_key(self, fname):

        pieces = fname.split("_")

        if "Session1" in pieces:
            return f"par1_{pieces[1]}"
        elif "Session2" in pieces:
            return f"par2.1_{pieces[2]}"
        elif "Session3" in pieces:
            return f"par2.2_{pieces[2]}"


    def load_shimmer_files(self):

        files = {}
        for fname in os.listdir(self.shimmer_dir):
            if fname.endswith(".csv"):
                dict_key = self.create_dict_key(fname)

                file = pd.read_csv(f"{self.shimmer_dir}{fname}", header=2, sep=",")
                if len(file.columns) == 5:
                    file.columns = ["Timestamp", "GSR_Range(No Unit)", "GSR_Skin_Conductance(uS)", "GSR_Skin_Resistance(kOhms)", "Junk"]
                else:
                    file.columns = ["Timestamp", "GSR_Range(No Unit)", "GSR_Skin_Conductance(uS)", "GSR_Skin_Resistance(kOhms)", "Marker", "Junk"]

                # Clean and add to dictionary.
                file = file.drop(["Junk"], axis=1)
                file["Timestamp"] = pd.to_datetime(file["Timestamp"])
                files[dict_key] = file
        return files



    def load_log_files(self):
        files = {}
        for fname in os.listdir(self.log_dir):
            if fname.endswith(".txt"):
                file = pd.read_csv(f"{self.log_dir}{fname}", skipfooter=2, sep=",", engine="python")
                file.columns = ["Timestamp", "Event", "Junk"]
                file = file.drop(["Junk"], axis=1)
                file["Timestamp"] = pd.to_datetime(file["Timestamp"])
                files[fname[:-4]] = file
        return files


    def place_event_markers(self, export=False, plot_each=False):

        for k, v in self.file_dict.items():
            print(k)
            pieces = k.split("_")
            if "par1" in pieces:
                logs = [self.log_dict["lucca_breath_1"], self.log_dict["lucca_startle_1"]]
            elif "par2.1" in pieces:
                logs = [self.log_dict["trev_breath_1"], self.log_dict["trev_startle_1"]]
            else:
                logs = [self.log_dict["trev_breath_2"], self.log_dict["trev_startle_2"]]

            if k == "par1_palm":
                v["Timestamp_Marks"] = self.create_ts_mark_col(logs, v, sample_rate=1024)
            else:
                v["Timestamp_Marks"] = self.create_ts_mark_col(logs, v)

            if export:
                if not os.path.exists(self.csv_path):
                    os.mkdir(self.csv_path)

                v.to_csv(f"{self.csv_path}{k}.csv")

            if plot_each:
                v["Timestamp_Marks"].plot()
                v["GSR_Skin_Conductance(uS)"].plot()
                plt.title(k.split('_')[1])
                plt.legend()
                plt.show()



    def create_ts_mark_col(self, logs, df, sample_rate=128):

        log_ts = logs[0]["Timestamp"].tolist() + logs[1]["Timestamp"].tolist()
        ts_list = df["Timestamp"].tolist()

        offset = log_ts[0] - ts_list[0]
        offset_samples = int(offset.total_seconds()) * sample_rate

        time_from_first_mark = [ts - log_ts[0] for ts in log_ts[1:]]
        marks = [int((ts.total_seconds() * sample_rate)) + offset_samples for ts in time_from_first_mark]
        marks.insert(0, offset_samples)
        marks.append(9999999)

        mark_index = 0
        mark_col = []
        for i in range(len(ts_list)):
            if i == marks[mark_index]:
                mark_col.append(5)
                mark_index += 1
            else:
                mark_col.append(0)

        return mark_col







tm = TimestampMatcher()
