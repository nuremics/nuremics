from __future__ import annotations

import os
import sys
from tkinter import filedialog
from tkinter import *

import json
import pandas as pd
from pathlib import Path

from .process import Process


class WorkFlow:
    """Manage workflow of processes."""
    
    def __init__(
        self,
        working_dir: Path,
        app_name: str,
        processes: list,
        erase: bool = True,
        verbose: bool = True,
    ):
        """Initialization."""
        
        # -------------------- #
        # Initialize variables #
        # -------------------- #
        self.app_name = app_name
        self.processes = processes
        self.diagram = {}
        self.erase = erase
        self.verbose = verbose

        # ---------------------- #
        # Define user parameters #
        # ---------------------- #
        user_params = []
        for _, process in enumerate(self.processes):
            for param in process["userParams"]:
                user_params.append(param)
        
        # Delete duplicates of parameters
        user_params = list(dict.fromkeys(user_params))

        # Add On/Off parameter to specify cases that should be executed
        user_params.append("EXECUTE")

        # ------------------------ #
        # Define working directory #
        # ------------------------ #
        if working_dir is None:
            root = Tk()
            root.withdraw()
            self.working_dir = Path(filedialog.askdirectory())
        else:
            self.working_dir = Path(working_dir)

        # ------------------------ #
        # Create working directory #
        # ------------------------ #
        self.working_dir.mkdir(
            exist_ok=True,
            parents=True,
        )

        # ----------------------- #
        # Go to working directory #
        # ----------------------- #
        os.chdir(self.working_dir)
        
        # ---------------------- #
        # Initialize inputs file #
        # ---------------------- #
        if not os.path.exists("inputs.xlsx"):
            
            # Create empty input dataframe
            self.df_inputs = pd.DataFrame(columns=["ID"]+user_params)
            
            # Write input dataframe
            self.df_inputs.to_excel("inputs.xlsx", index=False, sheet_name="user")
        
        else:
            
            # Read input dataframe
            self.df_inputs = pd.read_excel("inputs.xlsx", index_col=0)
            self.df_inputs.fillna(
                value="NA",
                inplace=True,
            )
        
        # Check if inputs dataframe is completed
        if user_params and self.df_inputs.empty:
            
            # Launch input file so that the user can fill it
            os.startfile("inputs.xlsx")
            
            # Stop application with message to the user
            sys.exit("INPUTS FILE MUST BE COMPLETED.")
        
        # ------------------------------------------ #
        # Initialize dictionary containing all paths #
        # ------------------------------------------ #
        try:
            with open("paths.json") as f:
                self.dict_paths = json.load(f)
        except:
            self.dict_paths = {}

    def __call__(self):
        """Launch workflow of processes."""
        
        # --------------- #
        # Launch workflow #
        # --------------- #
        for step, proc in enumerate(self.processes):
            
            # Define class object for the current process
            process = proc["process"]
            if "fixedParams" in proc:
                dict_fixed_params = proc["fixedParams"]
            else:
                dict_fixed_params = {}
            
            this_process:Process = process(
                df_inputs=self.df_inputs,
                dict_paths=self.dict_paths,
                params=proc["userParams"],
                dict_fixed_params=dict_fixed_params,
                erase=self.erase,
                is_processed=proc["execute"],
                verbose=proc["verbose"],
            )

            # Initialize build list
            this_process.build = []

            # Define process name
            if this_process.name is None:
                name = this_process.__class__.__name__
            else:
                name = this_process.name

            # Update list of parameters considering dependencies with previous processes
            if this_process.require is not None:
                for require in this_process.require:
                    for _, value in self.diagram.items():
                        if require in value.get("build"):
                            this_process.params = concat_lists_unique(
                                list1=this_process.params,
                                list2=value["params"],
                            )

            # Update process diagram
            self.diagram[name] = {
                "params": this_process.params,
                "build": this_process.build,
                "require": this_process.require,
            }

            # Printing
            print("---------------------------------------------------------")
            print("---------------------------------------------------------")
            print(f"| PROCESS {step+1} : {name}")
            print("---------------------------------------------------------")
            print("---------------------------------------------------------")

            # Define working folder associated to the current process
            folder_name = f"{step+1}_{name}"
            folder_path:Path = self.working_dir / folder_name
            folder_path.mkdir(exist_ok=True, parents=True)
            os.chdir(folder_path)

            if this_process.is_case:

                # Define sub-folders associated to each ID of the inputs dataframe
                for idx in this_process.df_params.index:

                    # Update process index
                    this_process.index = idx
                    
                    subfolder_path = self.working_dir / folder_name / str(idx)
                    subfolder_path.mkdir(exist_ok=True, parents=True)
                    os.chdir(subfolder_path)
                    
                    # Update dictionary of parameters for the current case ID
                    this_process.update_dict_params()

                    # Write json file containing current parameters
                    with open("parameters.json", "w") as f:
                        json.dump(this_process.dict_params, f, indent=4)

                    # Launch process
                    if this_process.is_processed:
                        print(">>> START <<<")
                        this_process()
                        print(">>> COMPLETED <<<")
                    else:
                        # Printing
                        print("> WARNING : Process is skipped /!\\")
                        print("---------------------------------------------------------")

                    # Go back to working folder
                    os.chdir(folder_path)
                
            else:
            
                # Launch process
                if this_process.is_processed:
                    print(">>> START <<<")
                    this_process()
                    print(">>> COMPLETED <<<")
                else:
                    # Printing
                    print(" > WARNING : Process is skipped /!\\")
                    print("---------------------------------------------------------")
            
            print("")

            # Update inputs dataframe and paths dictonary
            self.df_inputs = this_process.df_inputs
            self.dict_paths = this_process.dict_paths

            with open(os.path.join(self.working_dir, "paths.json"), "w") as f:
                json.dump(self.dict_paths, f, indent=4)
            
            # Go back to working directory
            os.chdir(self.working_dir)
        
        with open("diagram.json", "w") as f:
            json.dump(self.diagram, f, indent=4)


def concat_lists_unique(
    list1: list,
    list2: list,
):
    return list(dict.fromkeys(list1 + list2))