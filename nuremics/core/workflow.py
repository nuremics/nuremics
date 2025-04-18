from __future__ import annotations

import os
import sys
from tkinter import filedialog
from tkinter import *

import json
import pandas as pd
from pathlib import Path
from termcolor import colored

from .process import Process
from importlib.resources import files


class Application:
    """Create application."""
    
    def __init__(
        self,
        app_name:str = None,
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
            app_name=app_name,
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
        app_name: str,
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
        self.app_name = app_name
        self.dict_studies = {}
        self.processes = processes
        self.diagram = {}
        self.erase = erase
        self.verbose = verbose

        # ----------------------------------------------- #
        # Print ASCII NUREMICS logo with application name #
        # ----------------------------------------------- #
        ascii_logo_path:str = files("nuremics.resources").joinpath("logo.txt")
        f = open(ascii_logo_path, "r")
        for line in f:
            lines = f.readlines()
        print("")
        for line in lines:
            print(line.rstrip())

        print("")
        print(
            colored(f"| NUREMICS application : {self.app_name} |", "blue", attrs=["reverse"]),
        )

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
                    print("")
                    sys.exit(colored(f"(X) Please configure {study} in studies.json file (X)", "red"))

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
                print("")
                sys.exit(colored(f"(X) Please complete {study} parameters in inputs.csv file (X)", "red"))
            
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
                    sys.exit(colored(f"(X) Please complete {study} parameters in inputs.json file (X)", "red"))
        
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
        for n, study in enumerate(list(self.dict_studies.keys())):

            study_dir:Path = self.working_dir / study
            os.chdir(study_dir)

            for step, proc in enumerate(self.processes):
                
                # Define class object for the current process
                process = proc["process"]
                if "hardParams" in proc:
                    dict_hard_params = proc["hardParams"]
                else:
                    dict_hard_params = {}
                
                this_process:Process = process(
                    df_inputs=self.dict_variable_inputs[study],
                    dict_inputs=self.dict_fixed_inputs[study],
                    dict_paths=self.dict_paths[study],
                    params=proc["userParams"],
                    dict_hard_params=dict_hard_params,
                    erase=self.erase,
                    is_processed=proc["execute"],
                    verbose=proc["verbose"],
                    diagram=self.diagram,
                )
                this_process.init_params()

                # Define process name
                if this_process.name is None:
                    name = this_process.__class__.__name__
                else:
                    name = this_process.name

                # Define working folder associated to the current process
                folder_name = f"{step+1}_{name}"
                folder_path:Path = study_dir / folder_name
                folder_path.mkdir(exist_ok=True, parents=True)
                os.chdir(folder_path)

                if this_process.is_case:

                    # Define sub-folders associated to each ID of the inputs dataframe
                    for idx in this_process.df_params.index:
                        
                        # Printing
                        print("")
                        print(
                            colored(f"STUDY {n+1} :", "cyan", attrs=["underline"]),
                            colored(f"{study}", "cyan"),
                        )
                        print(
                            colored(f"PROCESS {step+1} :", "cyan", attrs=["underline"]),
                            colored(f"{name}", "cyan"),
                        )
                        print(
                            colored(f"DATASET :", "cyan", attrs=["underline"]),
                            colored(f"{idx}", "cyan"),
                        )

                        # Update process index
                        this_process.index = idx
                        
                        subfolder_path = study_dir / folder_name / str(idx)
                        subfolder_path.mkdir(exist_ok=True, parents=True)
                        os.chdir(subfolder_path)

                        # Launch process
                        if this_process.is_processed:
                            this_process()
                            this_process.finalize()
                        else:
                            # Printing
                            print("")
                            print(colored("/!\\ Process is skipped /!\\", "yellow"))

                        # Go back to working folder
                        os.chdir(folder_path)
                    
                else:

                    # Printing
                    print("")
                    print(
                        colored(f"STUDY {n+1} :", "cyan", attrs=["underline"]),
                        colored(f"{study}", "cyan"),
                    )
                    print(
                        colored(f"PROCESS {step+1} :", "cyan", attrs=["underline"]),
                        colored(f"{name}", "cyan"),
                    )
                
                    # Launch process
                    if this_process.is_processed:
                        this_process()
                        this_process.finalize()
                    else:
                        # Printing
                        print("")
                        print(colored("/!\\ Process is skipped /!\\", "yellow"))

                # Update process diagram
                self.diagram[name] = {
                    "params": this_process.params,
                    "allparams": this_process.allparams,
                    "build": this_process.build,
                    "require": this_process.require,
                }

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