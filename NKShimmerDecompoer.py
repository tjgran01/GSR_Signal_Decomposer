import neurokit2 as nk
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import os

from pathlib import Path
import platform

class NKShimmerDecomposer(object):
    def __init__(self, data_fname=None, data_fpath=Path(f"{os.getcwd()}/shimmer/"),
                 export_dir=Path(f"{os.getcwd()}/exports/"), show_fig=False,
                 save_fig=True, shimmer_file_sep="\t", sampling_rate=1000,
                 fig_dir=Path(f"{os.getcwd()}/exports/figs/"),
                 scr_col_name="Shimmer_92EE_GSR_Skin_Conductance_CAL",
                 shimmer_fname_string_tag="_Shimmer_"):
        """
        Decomposes raw SCR signal from SHIMMER Sensor and exports the decomposed
        values to a .csv. Optionally, plots the decomposed signal and saves the
        figure.

        Args:
            data_fname(str): If a data_fname is provided. The object will just
            decomepose that one file. It should be an absolute path of relative
            path to this file from where the code is run.

            data_fpath(pathlib.Path()): The path to the folder that contains all
            the SHIMMER files one wishes to decompose.

            export_dir(pathlib.Path()): The path to the export directory this class
            writes to. This is where decompose .csv files will be stored. Object
            will create this folder if it does not exist.

            show_fig(bool): True if you want to see figures of the decomposed
            signal while running.

            save_fig(bool): True if you want to save the figure generated. If
            both show_fig and save_fig are false then no figure will be generated.

            sampling_rate(int): Number of samples per second the SHIMMER was recording
            at.

            fig_dir(pathlib.Path()): The path to the folder that will contain all
            the exported figures. Object will create this folder if it does not
            exist.

            scr_col_name(str): The string name of the column in the SHIMMER export
            that houses the SCR data (I do not know if this varies from project to
            project).

            shimmer_fname_string_tag(str): A string identifier for the filename of
            the shimmer files. This ensures the object will only load files that
            contain the string this variable is set to.

        Returns:
            None: (Writes output files)

            ***If used in another project you can access the NKShimmerDecomposer.data_fnames
            and NKShimmerDecomposer.data_files to access the names of the signals and the
            NKShimmerDecomposer.decomposed_data to access the decomposed data.

            I would assign those to other variables and delete this object if you
            wish to go that route to free some memory.***
        """
        # Only used if you're passing a specific file --
        # Otherwise: checks ./shimmer/ dir.
        self.data_fname = data_fname
        self.data_fpath = data_fpath
        self.export_dir = export_dir
        self.fig_dir = fig_dir
        self.show_fig = show_fig
        self.save_fig = save_fig
        self.shimmer_file_sep = shimmer_file_sep
        self.sampling_rate = sampling_rate
        self.scr_col_name = scr_col_name
        self.shimmer_fname_string_tag = shimmer_fname_string_tag

        self.data_fnames, self.data_files = self.find_files()

        self.decomposed_data = []

        self.export_decomposed()


    def find_files(self):

        if self.data_fname == None:
            data_files = [self.load_data(Path(f"{self.data_fpath}/{data_fname}")) for data_fname in os.listdir(self.data_fpath) if self.shimmer_fname_string_tag in data_fname]
            data_fnames = [os.path.split(data_fname)[-1] for data_fname in os.listdir(self.data_fpath)]
        else:
            try:
                data_files = [self.load_data(self.data_fname)]
                data_fnames = [os.path.split(data_fname)[-1]]
            except FileNotFoundError:
                print(f"Could not locate file at path: {self.data_fname}.")
                print("Please type the relative path to the SHIMMER .csv File below.")
                while(True):
                    self.data_fname = input(">> ")
                    if os.path.exists(self.data_fname):
                        break
                    else:
                        print("That path does not seem to work either... ... CTRL + C to quit.")
                try:
                    data_files = [self.load_data(self.data_fname)]
                except:
                    print("The file path provided still does not seem to want to load. Closing applicaiton.")

        return data_fnames, data_files


    def load_data(self, data_fpath):

        # Read datafile.
        data = pd.read_csv(data_fpath, header=1, sep=self.shimmer_file_sep,
                           low_memory=False)

        # Remove first row --- Shimmer's first row is units. Which makes pandas
        # import every column as a array of strings. We hate this and want it dead.
        data = data.drop(0, axis=0)

        # Convert columns to floats (pandas pulls in as strings because of the
        # label col removed above).
        for col in data.columns:
            data[f"{col}"] = data[f"{col}"].astype("float")

        return data


    def make_export_directories(self):

        for dir in [self.export_dir, self.fig_dir]:
            if not os.path.exists(dir):
                os.makedirs(dir)


    def export_decomposed(self):

        self.make_export_directories()

        for i, data in enumerate(self.data_files):
            # Decomposition happens in this line.
            eda = nk.eda_phasic(nk.standardize(data[self.scr_col_name]),
                                sampling_rate=self.sampling_rate)

            self.decomposed_data.append(eda)

            if self.save_fig:
                eda.plot()
                plt.savefig(Path(f"{self.fig_dir}/{self.data_fnames[i][:-4]}.png"), dpi=500)
                if self.show_fig:
                    plt.show()

            # Save decomposed df
            eda.to_csv(Path(f"{self.export_dir}/{self.data_fnames[i][:-4]}_DECOMPOSED.csv"))



if __name__ == "__main__":
    decompser = NKShimmerDecomposer()
