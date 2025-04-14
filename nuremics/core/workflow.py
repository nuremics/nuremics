from __future__ import annotations

import os
import sys
from tkinter import filedialog
from tkinter import *

import json
import pandas as pd
from pathlib import Path

from .process import Process


class Application:
    """Create application."""
    
    def __init__(
        self,
        working_dir: Path = None,
        processes: list = None,
        studies: list = None,
        erase: bool = True,
        verbose: bool = True,
    ):
        # ---------------------- #
        # Define workflow object #
        # ---------------------- #
        self.workflow = WorkFlow(
            working_dir=working_dir,
            processes=processes,
            studies=studies,
            erase=erase,
            verbose=verbose,
        )

    def __call__(self):
        
        # --------------- #
        # Launch workflow #
        # --------------- #
        self.workflow()


class WorkFlow:
    """Manage workflow of processes."""
    
    def __init__(
        self,
        working_dir: Path,
        processes: list,
        studies: list = None,
        erase: bool = True,
        verbose: bool = True,
    ):
        """Initialization."""
        
        # -------------------- #
        # Initialize variables #
        # -------------------- #
        self.dict_studies = {}
        self.processes = processes
        self.diagram = {}
        self.erase = erase
        self.verbose = verbose

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
        # Define user parameters #
        # ---------------------- #
        user_params = []
        for _, process in enumerate(self.processes):
            for param in process["userParams"]:
                user_params.append(param)
        
        # Delete duplicates of parameters
        user_params = list(dict.fromkeys(user_params))

        # ------------------ #
        # Initialize studies #
        # ------------------ #
        if os.path.exists("studies.json"):
            with open("studies.json") as f:
                self.dict_studies = json.load(f)
        
        # Clean studies
        for study in list(self.dict_studies.keys()):
            if study not in studies:
                del self.dict_studies[study]
        
        # Clean parameters
        for study in list(self.dict_studies.keys()):
            for param in list(self.dict_studies[study]["params"]):
                if param not in user_params:
                    del self.dict_studies[study]["params"][param]

        # Initialize parameters
        for study in studies:
            
            if study not in self.dict_studies:
                self.dict_studies[study] = {
                    "execute": True,
                    "params": {},
                }
            
            for param in user_params:
                if param not in self.dict_studies[study]["params"]:
                    self.dict_studies[study]["params"][param] = None

        # Write studies json file
        with open("studies.json", "w") as f:
            json.dump(self.dict_studies, f, indent=4)
        
        # Check if studies json has been properly completed
        for study in studies:
            for param in user_params:
                if self.dict_studies[study]["params"][param] is None:
                    sys.exit(f"/!\\ {study} must be configured /!\\")

        # -------------------- #
        # Initialize data tree #
        # -------------------- #
        self.dict_fixed_inputs = {}
        self.dict_variable_inputs = {}
        self.dict_paths = {}
        for study in studies:

            # Create study directory
            study_dir:Path = self.working_dir / study
            study_dir.mkdir(
                exist_ok=True,
                parents=True,
            )

            # Define list of fixed/variable parameters
            fixed_params = []
            variable_params = []
            for key, value in self.dict_studies[study]["params"].items():
                if value is True:
                    variable_params.append(key)
                else:
                    fixed_params.append(key)

            # Define inputs dataframe with variable parameters
            if not os.path.exists(f"{study}/inputs.csv"):

                # Create empty input dataframe
                df_inputs = pd.DataFrame(columns=["ID"]+variable_params+["EXECUTE"])

                # Write input dataframe
                df_inputs.to_csv(
                    path_or_buf=f"{study}/inputs.csv",
                    index=False,
                )

            else:
                
                # Read input dataframe
                df_inputs = pd.read_csv(
                    filepath_or_buffer=f"{study}/inputs.csv",
                    index_col=0
                )
                df_inputs.fillna(
                    value="NA",
                    inplace=True,
                )
            
            # Update inputs dictionary with variable parameters
            self.dict_variable_inputs[study] = df_inputs

            # Check if variable input parameters have been defined
            if df_inputs.empty:
                sys.exit(f"/!\\ Please complete {study} parameters in inputs.csv file /!\\")
            
            # Define inputs dictionary with fixed parameters
            if not os.path.exists(f"{study}/inputs.json"):

                dict_inputs = {}
                for param in fixed_params:
                    dict_inputs[param] = None
                
                with open(f"{study}/inputs.json", "w") as f:
                    json.dump(dict_inputs, f, indent=4)
            
            else:

                with open(f"{study}/inputs.json") as f:
                    dict_inputs = json.load(f)

            # Update inputs dictionary with fixed parameters
            self.dict_fixed_inputs[study] = dict_inputs

            # Check if fixed input parameters have been defined
            for key, value in dict_inputs.items():
                if value is None:
                    sys.exit(f"/!\\ Please complete {study} parameters in inputs.json file /!\\")
        
            # Initialize dictionary containing all paths
            try:
                with open(f"{study}/paths.json") as f:
                    dict_paths = json.load(f)
            except:
                dict_paths = {}
            
            self.dict_paths[study] = dict_paths

    def __call__(self):
        """Launch workflow of processes."""
        
        # --------------- #
        # Launch workflow #
        # --------------- #
        for study in list(self.dict_studies.keys()):

            # Printing
            print("---------------------------------------------------------")
            print("---------------------------------------------------------")
            print(f"| STUDY : {study}")
            print("---------------------------------------------------------")
            print("---------------------------------------------------------")
            print("")

            study_dir:Path = self.working_dir / study
            os.chdir(study_dir)

            for step, proc in enumerate(self.processes):
                
                # Define class object for the current process
                process = proc["process"]
                if "fixedParams" in proc:
                    dict_fixed_params = proc["fixedParams"]
                else:
                    dict_fixed_params = {}
                
                this_process:Process = process(
                    df_inputs=self.dict_variable_inputs[study],
                    dict_inputs=self.dict_fixed_inputs[study],
                    dict_paths=self.dict_paths[study],
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

                # Update process diagram
                self.diagram[name] = {
                    "params": this_process.params,
                    "build": this_process.build,
                    "require": this_process.require,
                }

                # Printing
                print("---------------------------------------------------------")
                print(f"| PROCESS {step+1} : {name}")
                print("---------------------------------------------------------")

                # Define working folder associated to the current process
                folder_name = f"{step+1}_{name}"
                folder_path:Path = study_dir / folder_name
                folder_path.mkdir(exist_ok=True, parents=True)
                os.chdir(folder_path)

                if this_process.is_case:

                    # Define sub-folders associated to each ID of the inputs dataframe
                    for idx in this_process.df_params.index:

                        # Update process index
                        this_process.index = idx
                        
                        subfolder_path = study_dir / folder_name / str(idx)
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

                # Update paths dictonary
                self.dict_paths[study] = this_process.dict_paths

                with open(os.path.join(self.working_dir, f"{study}/paths.json"), "w") as f:
                    json.dump(self.dict_paths[study], f, indent=4)
                
                # Go back to study directory
                os.chdir(study_dir)
            
            with open("diagram.json", "w") as f:
                json.dump(self.diagram, f, indent=4)
        
        # Go back to working directory
        os.chdir(self.working_dir)