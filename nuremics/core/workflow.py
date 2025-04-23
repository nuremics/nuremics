from __future__ import annotations

import os
import sys
from tkinter import filedialog
from tkinter import *

import json
import shutil
import numpy as np
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

        self.workflow.print_logo()
        self.workflow.print_application()
        self.workflow.print_processes()

        self.workflow.init_studies()
        self.workflow.test_studies_settings()
        self.workflow.print_studies()

        self.workflow.configure_inputs()
        self.workflow.init_data_tree()

        self.workflow.set_inputs()
        self.workflow.test_inputs_settings()

        print(self.workflow.fixed_params_messages)
        print(self.workflow.fixed_inputfiles_messages)
        print(self.workflow.fixed_params_config)
        print(self.workflow.fixed_inputfiles_config)

        print(self.workflow.variable_params_messages)
        print(self.workflow.variable_inputfiles_messages)
        print(self.workflow.variable_params_config)
        print(self.workflow.variable_inputfiles_config)

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
        studies: list = ["Default"],
        erase: bool = True,
        verbose: bool = True,
    ):
        """Initialization."""

        # -------------------- #
        # Initialize variables #
        # -------------------- #
        self.app_name = app_name
        self.studies = studies
        self.dict_studies = {}
        self.processes = processes
        self.user_params = []
        self.inputfiles = []
        self.studies_messages = {}
        self.studies_config = {}
        self.fixed_params_messages = {}
        self.fixed_params_config = {}
        self.fixed_inputfiles_messages = {}
        self.fixed_inputfiles_config = {}
        self.variable_params_messages = {}
        self.variable_params_config = {}
        self.variable_inputfiles_messages = {}
        self.variable_inputfiles_config = {}
        self.fixed_params = {}
        self.fixed_inputfiles = {}
        self.variable_params = {}
        self.variable_inputfiles = {}
        self.dict_fixed_params = {}
        self.dict_variable_params = {}
        self.dict_inputfiles = {}
        self.dict_paths = {}
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
        for _, process in enumerate(self.processes):
            for param in process["userParams"]:
                self.user_params.append(param)

        # Delete duplicates of parameters
        self.user_params = list(dict.fromkeys(self.user_params))

        # ---------------------- #
        # Define user inputfiles #
        # ---------------------- #
        for _, process in enumerate(self.processes):
            if "inputfiles" in process:
                for file in process["inputfiles"]:
                    self.inputfiles.append(file)
        
        # Delete duplicates of inputfiles
        self.inputfiles = list(dict.fromkeys(self.inputfiles))

        # # -------------------- #
        # # Initialize data tree #
        # # -------------------- #
        # print("")
        # print(
        #     colored("> DATASETS <", "blue", attrs=["reverse"]),
        # )
        # for study in self.studies:

        #     # Printing
        #     print("")
        #     print(colored(f"| {study} |", "magenta"))

        #     # Go to study directory
        #     os.chdir(study_dir)

        #     self.dict_inputfiles[study] = {}
        #     self.init_fixed_inputs(study)
        #     self.init_variable_inputs(study)

        #     # -------------------------------------------#
        #     # Initialize dictionary containing all paths #
        #     # -------------------------------------------#
        #     try:
        #         with open("paths.json") as f:
        #             dict_paths = json.load(f)
        #     except:
        #         dict_paths = {}
            
        #     self.dict_paths[study] = dict_paths

        #     # Go back to working directory
        #     os.chdir(self.working_dir)

    def print_logo(self):
        """Print ASCII NUREMICS logo"""

        ascii_logo_path:str = files("nuremics.resources").joinpath("logo.txt")
        f = open(ascii_logo_path, "r")
        for line in f:
            lines = f.readlines()
        print("")
        for line in lines:
            print(line.rstrip())

    def print_application(self):
        """Print application name"""

        print("")
        print(
            colored("> APPLICATION <", "blue", attrs=["reverse"]),
        )
        print("")
        print(
            colored(self.app_name, "blue"),
        )

    def print_processes(self):
        """Print processes"""

        print("")
        print(
            colored("> PROCESSES <", "blue", attrs=["reverse"]),
        )
        print("")
        for i, process in enumerate(self.processes):
            text_inputs = ""
            if "userParams" in process:
                for param in process["userParams"]:
                    if text_inputs == "": text_inputs += param
                    else: text_inputs += ", "+param
            if "inputfiles" in process:
                for file in process["inputfiles"]:
                    if text_inputs == "": text_inputs += file
                    else: text_inputs += ", "+file
            text_inputs += "."
            print(
                colored(f"{i+1}. {process["process"].__name__}, with inputs : {text_inputs}", "blue"),
            )

    def init_studies(self):
        """Initialize studies"""

        # Open studies json fil if existing
        if os.path.exists("studies.json"):
            with open("studies.json") as f:
                self.dict_studies = json.load(f)
        
        # Clean studies
        for study in list(self.dict_studies.keys()):
            if study not in self.studies:
                del self.dict_studies[study]
        
        # Clean parameters
        for study in list(self.dict_studies.keys()):
            for param in list(self.dict_studies[study]["params"]):
                if param not in self.user_params:
                    del self.dict_studies[study]["params"][param]
        
        # Clean inputfiles
        for study in list(self.dict_studies.keys()):
            for file in list(self.dict_studies[study]["inputfiles"]):
                if file not in self.inputfiles:
                    del self.dict_studies[study]["inputfiles"][file]
        
        # Initialize parameters/inputfiles
        for study in self.studies:
            
            if study not in self.dict_studies:
                self.dict_studies[study] = {
                    "execute": True,
                    "params": {},
                    "inputfiles": {},
                }
            
            for param in self.user_params:
                if param not in self.dict_studies[study]["params"]:
                    if study == "Default":
                        self.dict_studies[study]["params"][param] = False
                    else:
                        self.dict_studies[study]["params"][param] = None
            
            for file in self.inputfiles:
                if file not in self.dict_studies[study]["inputfiles"]:
                    if study == "Default":
                        self.dict_studies[study]["inputfiles"][file] = False
                    else:
                        self.dict_studies[study]["inputfiles"][file] = None

        # Write studies json file
        with open("studies.json", "w") as f:
            json.dump(self.dict_studies, f, indent=4)

    def test_studies_settings(self):
        """Check if studies has been properly configured"""
        
        for study in self.studies:

            self.studies_messages[study] = []
            self.studies_config[study] = True

            for param in self.user_params:
                if self.dict_studies[study]["params"][param] is None:
                    self.studies_messages[study].append(f"(X) {param} not configured.")
                    self.studies_config[study] = False
                else:
                    if self.dict_studies[study]["params"][param]: text = "variable"
                    else: text = "fixed"
                    self.studies_messages[study].append(f"(V) {param} is {text}.")

            for file in self.inputfiles:
                if self.dict_studies[study]["inputfiles"][file] is None:
                    self.studies_messages[study].append(f"(X) {file} not configured.")
                    self.studies_config[study] = False
                else:
                    if self.dict_studies[study]["inputfiles"][file]: text = "variable"
                    else: text = "fixed"
                    self.studies_messages[study].append(f"(V) {file} is {text}.")

    def print_studies(self):
        """Print studies"""

        print("")
        print(
            colored("> STUDIES <", "blue", attrs=["reverse"]),
        )
        for study in self.studies:

            # Printing
            print("")
            print(
                colored(f"| {study} |", "magenta"),
            )

            for message in self.studies_messages[study]:
                if "(V)" in message: print(colored(message, "green"))
                elif "(X)" in message: print(colored(message, "red"))
        
            if not self.studies_config[study]:
                print("")
                print(colored(f"(X) Please configure file :", "red"))
                print(colored(f"> {str(Path.cwd() / "studies.json")}", "red"))
                sys.exit()

    def configure_inputs(self):
       """Configure inputs with lists of fixed/variable parameters/inputfiles"""

       for study in self.studies:

            # Define list of fixed/variable parameters
            fixed_params = []
            variable_params = []
            for key, value in self.dict_studies[study]["params"].items():
                if value is True: variable_params.append(key)
                else: fixed_params.append(key)
            
            # Define list of fixed/variable inputfiles
            fixed_inputfiles = []
            variable_inputfiles = []
            for key, value in self.dict_studies[study]["inputfiles"].items():
                if value is True: variable_inputfiles.append(key)
                else: fixed_inputfiles.append(key)
            
            self.fixed_params[study] = fixed_params
            self.variable_params[study] = variable_params
            self.fixed_inputfiles[study] = fixed_inputfiles
            self.variable_inputfiles[study] = variable_inputfiles

    def init_data_tree(self):
        """Initialize data tree"""

        for study in self.studies:

            # Initialize study directory
            study_dir:Path = self.working_dir / study
            study_dir.mkdir(
                exist_ok=True,
                parents=True,
            )

            # Initialize inputs csv
            inputs_file:Path = study_dir / "inputs.csv"
            if (len(self.variable_params[study]) > 0) or \
               (len(self.variable_inputfiles[study]) > 0):
                
                if not inputs_file.exists():

                    # Create empty input dataframe
                    df_inputs = pd.DataFrame(columns=["ID"]+self.variable_params[study]+["EXECUTE"])

                    # Write input dataframe
                    df_inputs.to_csv(
                        path_or_buf=inputs_file,
                        index=False,
                    )

                else:
                    
                    # Read input dataframe
                    df_inputs = pd.read_csv(
                        filepath_or_buffer=inputs_file,
                        index_col=0,
                    )

                    # Update variable parameters
                    df_inputs = df_inputs.assign(**{param: np.nan for param in self.variable_params[study] if param not in df_inputs.columns})
                    df_inputs = df_inputs[[col for col in self.variable_params[study] if col in df_inputs.columns] + ["EXECUTE"]]

                    # Write input dataframe
                    df_inputs.to_csv(
                        path_or_buf=inputs_file,
                    )

            else:
                # Delete file
                if inputs_file.exists(): inputs_file.unlink()

            # Initialize inputs directory
            inputs_dir:Path = study_dir / "0_inputs"
            if len(self.inputfiles) > 0:

                # Create inputs directory (if necessary)
                inputs_dir.mkdir(
                    exist_ok=True,
                    parents=True,
                )

                # Delete fixed inputfiles (if necessary)
                inputs_files = [f for f in inputs_dir.iterdir() if f.is_file()]
                for file in inputs_files:
                    if os.path.split(file)[-1] not in self.fixed_inputfiles[study]:
                        file.unlink()
                
                # Update inputs subfolders for variable inputfiles
                if len(self.variable_inputfiles[study]) > 0:

                    # Create subfolders (if necessary)    
                    for index in df_inputs.index:
                        
                        inputs_subfolder:Path = inputs_dir / index
                        inputs_subfolder.mkdir(
                            exist_ok=True,
                            parents=True,
                        )

                        # Delete variable inputfiles (if necessary)
                        inputs_files = [f for f in inputs_subfolder.iterdir() if f.is_file()]
                        for file in inputs_files:
                            if os.path.split(file)[-1] not in self.variable_inputfiles[study]:
                                file.unlink()
                    
                    # Delete subfolders (if necessary)
                    inputs_subfolders = [f for f in inputs_dir.iterdir() if f.is_dir()]
                    for folder in inputs_subfolders:
                        id = os.path.split(folder)[-1]
                        if id not in df_inputs.index.tolist():
                            shutil.rmtree(folder)
                
                else:

                    # Delete all inputs subfolders (if necessary)
                    inputs_subfolders = [f for f in inputs_dir.iterdir() if f.is_dir()]
                    for folder in inputs_subfolders:
                        shutil.rmtree(folder)

            else:
                # Delete inputs directory (if necessary)
                if inputs_dir.exists(): shutil.rmtree(inputs_dir)

            # Initialize inputs json file
            inputs_file:Path = study_dir / "inputs.json"
            if len(self.fixed_params[study]) > 0:

                # Create file
                if not inputs_file.exists():

                    # Initialize dictionary
                    dict_inputs = {}
                    for param in self.fixed_params[study]:
                        dict_inputs[param] = None
                    
                    # Write json
                    with open(inputs_file, "w") as f:
                        json.dump(dict_inputs, f, indent=4)
                
                # Update file
                else:

                    # Read json with fixed parameters
                    with open(inputs_file) as f:
                        dict_inputs = json.load(f)
                    
                    # Update fixed parameters
                    dict_inputs = {k: dict_inputs.get(k, None) for k in self.fixed_params[study]}

                    # Write json
                    with open(inputs_file, "w") as f:
                        json.dump(dict_inputs, f, indent=4)
            
            else:
                
                # Delete file
                if inputs_file.exists(): inputs_file.unlink()

    def set_inputs(self):
        """Set all inputs"""

        # Loop over studies
        for study in self.studies:

            # Define study directory
            study_dir:Path = self.working_dir / study
            
            # Go to study directory
            os.chdir(study_dir)

            # Initialize inputfiles dictionary
            self.dict_inputfiles[study] = {}

            # Fixed parameters 
            if len(self.fixed_params[study]) > 0:

                # Read json
                with open("inputs.json") as f:
                    self.dict_fixed_params[study] = json.load(f)
            
            else:
                self.dict_fixed_params[study] = {}

            # Fixed inputfiles
            dict_inputfiles = {}
            for file in self.fixed_inputfiles[study]:
                key = os.path.splitext(file)[0]
                dict_inputfiles[key] = str(Path(os.getcwd()) / "0_inputs" / file)

            self.dict_inputfiles[study] = {**self.dict_inputfiles[study], **dict_inputfiles}

            # Variable parameters
            if (len(self.variable_params[study]) > 0) or \
               (len(self.variable_inputfiles[study]) > 0):
                
                # Read input dataframe
                self.dict_variable_params[study] = pd.read_csv(
                    filepath_or_buffer="inputs.csv",
                    index_col=0,
                )
            
            else:
                self.dict_variable_params[study] = pd.DataFrame()
            
            # Variable inputfiles
            if len(self.variable_inputfiles[study]) > 0:
                
                dict_inputfiles = {}
                df_inputs = pd.read_csv(
                    filepath_or_buffer="inputs.csv",
                    index_col=0,
                )
                for file in self.variable_inputfiles[study]:
                    key = os.path.splitext(file)[0]
                    dict_inputfiles[key] = {}
                    for idx in df_inputs.index:
                        dict_inputfiles[key][idx] = str(Path(os.getcwd()) / "0_inputs" / idx / file)

                self.dict_inputfiles[study] = {**self.dict_inputfiles[study], **dict_inputfiles}

            # Go back to working directory
            os.chdir(self.working_dir)        

    def test_inputs_settings(self):
        """Test that inputs have been properly set"""

        # Loop over studies
        for study in self.studies:

            # Define study directory
            study_dir:Path = self.working_dir / study
            
            # Go to study directory
            os.chdir(study_dir)

            self.fixed_params_messages[study] = []
            self.fixed_inputfiles_messages[study] = []
            self.variable_params_messages[study] = {}
            self.variable_inputfiles_messages[study] = {}
            self.fixed_params_config[study] = True
            self.fixed_inputfiles_config[study] = True
            self.variable_params_config[study] = {}
            self.variable_inputfiles_config[study] = {}
            
            # Fixed parameters
            for param, value in self.dict_fixed_params[study].items():
                if value is None:
                    self.fixed_params_messages[study].append(f"(X) {param}")
                    self.fixed_params_config[study] = False
                else:
                    self.fixed_params_messages[study].append(f"(V) {param}")
            
            # Fixed inputfiles
            for file in self.fixed_inputfiles[study]:
                file_path:Path = Path("0_inputs") / file
                if not file_path.exists():
                    self.fixed_inputfiles_messages[study].append(f"(X) {file}")
                    self.fixed_inputfiles_config[study] = False
                else:
                    self.fixed_inputfiles_messages[study].append(f"(V) {file}")

            # Variable inputs
            if (len(self.variable_params[study]) > 0) or \
               (len(self.variable_inputfiles[study]) > 0):

                for index in self.dict_variable_params[study].index:

                    inputs_dir:Path = Path("0_inputs") / index

                    self.variable_params_messages[study][index] = []
                    self.variable_inputfiles_messages[study][index] = []
                    self.variable_params_config[study][index] = True
                    self.variable_inputfiles_config[study][index] = True
                    
                    # Variable parameters
                    for param in self.variable_params[study]:
                        value = self.dict_variable_params[study].at[index, param]
                        if pd.isna(value) or value == "":
                            self.variable_params_messages[study][index].append(f"(X) {param}")
                            self.variable_params_config[study][index] = False
                        else:
                            self.variable_params_messages[study][index].append(f"(V) {param}")

                    # Variable inputfiles
                    for file in self.variable_inputfiles[study]:
                        file_path:Path = inputs_dir / file
                        if not file_path.exists():
                            self.variable_inputfiles_messages[study][index].append(f"(X) {file}")
                            self.variable_inputfiles_config[study][index] = False
                        else:
                            self.variable_inputfiles_messages[study][index].append(f"(V) {file}")
            
            # Go back to working directory
            os.chdir(self.working_dir) 

    def init_fixed_inputs(self,
        study: str,
    ):
        """Define inputs dictionary with fixed parameters/inputfiles"""

        self.dict_fixed_params[study] = {}
        

        # ---------- #
        # Inputfiles #
        # ---------- #
        dict_inputfiles = {}
        for file in self.fixed_inputfiles[study]:
            key = os.path.splitext(file)[0]
            dict_inputfiles[key] = str(Path(os.getcwd()) / "0_inputs" / file)

        self.dict_inputfiles[study] = {**self.dict_inputfiles[study], **dict_inputfiles}

        # --------------------------------------- #
        # Check if fixed inputs have been defined #
        # --------------------------------------- #
        list_text = [colored(f"> Common :", "blue")]
        list_errors = []
        config = True
        for param, value in self.dict_fixed_params[study].items():
            if value is None:
                list_text.append(colored(f"(X) {param}", "red"))
                if config:
                    list_errors.append(colored(f"> {str(Path.cwd() / "inputs.json")}", "red"))
                config = False
            else:
                list_text.append(colored(f"(V) {param}", "green"))
        
        for file in self.fixed_inputfiles[study]:
            file_path:Path = Path("0_inputs") / file
            if not file_path.exists():
                list_text.append(colored(f"(X) {file}", "red"))
                list_errors.append(colored(f"> {str(Path.cwd() / "0_inputs" / file)}", "red"))
            else:
                list_text.append(colored(f"(V) {file}", "green"))
            
        # Printing
        print(*list_text)
        
        if len(list_errors) > 0:
            print("")
            print(colored(f"(X) Please configure file(s) :", "red"))
            for error in list_errors:
                print(error)
            sys.exit()

    def init_variable_inputs(self,
        study,
    ):
        """Define inputs dictionary with variable parameters/inputfiles"""

        # ----------------------- #
        # Define inputs dataframe #
        # ----------------------- #
        if (len(self.variable_params[study]) > 0) or \
           (len(self.variable_inputfiles[study]) > 0):
            
            # Read input dataframe
            df_inputs = pd.read_csv(
                filepath_or_buffer="inputs.csv",
                index_col=0,
            )

            # ---------- #
            # Inputfiles #
            # ---------- #
            dict_inputfiles = {}
            for file in self.variable_inputfiles[study]:
                key = os.path.splitext(file)[0]
                dict_inputfiles[key] = {}
                for idx in df_inputs.index:
                    dict_inputfiles[key][idx] = str(Path(os.getcwd()) / "0_inputs" / idx / file)

            self.dict_inputfiles[study] = {**self.dict_inputfiles[study], **dict_inputfiles}

            # Delete useless input folders / files
            if len(self.inputfiles) > 0:
                
                input_folders = [f for f in Path("0_inputs").iterdir() if f.is_dir()]
                for folder in input_folders:
                    
                    id = os.path.split(folder)[-1]
                    if id not in df_inputs.index.tolist():
                        shutil.rmtree(folder)
                    
                    path = Path("0_inputs") / id
                    input_files = [f for f in path.iterdir() if f.is_file()]
                    for file in input_files:
                        if os.path.split(file)[-1] not in self.variable_inputfiles[study]:
                            file.unlink()
            
            # Check if datasets have been defined
            if len(df_inputs.index) == 0:
                print("")
                print(colored(f"(X) Please define at least one dataset in file :", "red"))
                print(colored(f"> {str(Path.cwd() / "inputs.csv")}", "red"))
                sys.exit()

            list_errors = []
            config = True
            for index in df_inputs.index:

                # Create inputs folder (if necessary)
                if len(self.variable_inputfiles[study]) > 0:
                    inputs_dir:Path = Path("0_inputs") / index
                    inputs_dir.mkdir(
                        exist_ok=True,
                        parents=True,
                    )

                list_text = [colored(f"> {index} :", "blue")]
                for param in self.variable_params[study]:
                    value = df_inputs.at[index, param]
                    if pd.isna(value) or value == "":
                        list_text.append(colored(f"(X) {param}", "red"))
                        if config:
                            list_errors.append(colored(f"> {str(Path.cwd() / "inputs.csv")}", "red"))
                        config = False
                    else:
                        list_text.append(colored(f"(V) {param}", "green"))

                for file in self.variable_inputfiles[study]:
                    file_path:Path = inputs_dir / file
                    if not file_path.exists():
                        list_text.append(colored(f"(X) {file}", "red"))
                        list_errors.append(colored(f"> {str(Path.cwd() / "0_inputs" / index / file)}", "red"))
                    else:
                        list_text.append(colored(f"(V) {file}", "green"))

                # Printing
                print(*list_text)
        
            list_errors = sorted(list_errors, key=lambda x: '0_inputs' in x)

            if len(list_errors) > 0:
                print("")
                print(colored(f"(X) Please configure file(s) :", "red"))
                for error in list_errors:
                    print(error)
                sys.exit()

            # Update inputs dictionary with variable parameters
            self.dict_variable_params[study] = df_inputs
        
        else:

            if os.path.exists("inputs.csv"):
                Path("inputs.csv").unlink()
            
            self.dict_variable_params[study] = pd.DataFrame()

    def __call__(self):
        """Launch workflow of processes."""
        
        # --------------- #
        # Launch workflow #
        # --------------- #
        print("")
        print(
            colored("> RUNNING <", "blue", attrs=["reverse"]),
        )

        for study in list(self.dict_studies.keys()):

            study_dir:Path = self.working_dir / study
            os.chdir(study_dir)

            for step, proc in enumerate(self.processes):
                
                # Define class object for the current process
                process = proc["process"]
                if "hardParams" in proc:
                    dict_hard_params = proc["hardParams"]
                else:
                    dict_hard_params = {}
                
                if "userParams" in proc: user_params = proc["userParams"]
                else: user_params = []
                if "inputfiles" in proc: inputfiles = proc["inputfiles"]
                else: inputfiles = []

                this_process:Process = process(
                    df_inputs=self.dict_variable_params[study],
                    dict_inputs=self.dict_fixed_params[study],
                    dict_inputfiles=self.dict_inputfiles[study],
                    dict_paths=self.dict_paths[study],
                    params=user_params,
                    inputfiles=inputfiles,
                    dict_hard_params=dict_hard_params,
                    fixed_params=self.fixed_params[study],
                    variable_params=self.variable_params[study],
                    fixed_inputfiles=self.fixed_inputfiles[study],
                    variable_inputfiles=self.variable_inputfiles[study],
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
                            colored(f"| {study} | {name} | {idx} |", "magenta"),
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
                            print(colored("(!) Process is skipped.", "yellow"))

                        # Go back to working folder
                        os.chdir(folder_path)
                    
                else:

                    # Printing
                    print("")
                    print(
                        colored(f"| {study} | {name} |", "magenta"),
                    )
                
                    # Launch process
                    if this_process.is_processed:
                        this_process()
                        this_process.finalize()
                    else:
                        # Printing
                        print("")
                        print(colored("(!) Process is skipped.", "yellow"))

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