from __future__ import annotations

import os
import sys
import attrs
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
        workflow: list = None,
        studies: list = None,
        verbose: bool = True,
    ):
        # ---------------------- #
        # Define workflow object #
        # ---------------------- #
        self.workflow = WorkFlow(
            app_name=app_name,
            working_dir=working_dir,
            processes=workflow,
            studies=studies,
            verbose=verbose,
        )

        self.workflow.print_logo()
        self.workflow.print_application()

        self.workflow.get_params_type()
        self.workflow.print_processes()

        self.workflow.init_studies()
        self.workflow.test_studies_modification()
        self.workflow.test_studies_settings()
        self.workflow.print_studies()

        self.workflow.configure_inputs()
        self.workflow.init_data_tree()

        self.workflow.init_process_settings()

        self.workflow.set_inputs()
        self.workflow.test_inputs_settings()
        self.workflow.print_inputs()

        self.workflow.init_paths()

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
        verbose: bool = True,
    ):
        """Initialization."""

        # -------------------- #
        # Initialize variables #
        # -------------------- #
        self.app_name = app_name
        self.studies = studies
        self.processes = processes
        self.list_processes = []
        self.dict_studies = {}
        self.dict_process = {}
        self.input_params = []
        self.input_paths = []
        self.params_type = {}
        self.studies_modif = {}
        self.studies_messages = {}
        self.studies_config = {}
        self.fixed_params_messages = {}
        self.fixed_params_config = {}
        self.fixed_paths_messages = {}
        self.fixed_paths_config = {}
        self.variable_params_messages = {}
        self.variable_params_config = {}
        self.variable_paths_messages = {}
        self.variable_paths_config = {}
        self.fixed_params = {}
        self.fixed_paths = {}
        self.variable_params = {}
        self.variable_paths = {}
        self.dict_fixed_params = {}
        self.dict_variable_params = {}
        self.dict_input_paths = {}
        self.dict_paths = {}
        self.diagram = {}
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

        # ----------------------- #
        # Define input parameters #
        # ----------------------- #
        for _, process in enumerate(self.processes):
            if "input_params" in process:
                for param in list(process["input_params"].values()):
                    self.input_params.append(param)

        # Delete duplicates of parameters
        self.input_params = list(dict.fromkeys(self.input_params))

        # ------------------ #
        # Define input paths #
        # ------------------ #
        for _, process in enumerate(self.processes):
            if "input_paths" in process:
                for file in list(process["input_paths"].values()):
                    self.input_paths.append(file)
        
        # Delete duplicates of paths
        self.input_paths = list(dict.fromkeys(self.input_paths))

        # ------------------------ #
        # Define list of processes #
        # ------------------------ #
        for proc in self.processes:
            self.list_processes.append(proc["process"].__name__)

    def get_params_type(self):

        for proc in self.processes:

            process = proc["process"]
            name = proc["process"].__name__
            this_process:Process = process()

            self.params_type[name] = {}
            for key, value_type in this_process.__class__.__annotations__.items():
                # Get the module and type name
                module_name = value_type.__module__
                type_name = value_type.__name__

                # Format depending on whether it's a built-in type or not
                if ("input_params" in proc) and (key in proc["input_params"]):
                    if module_name == "builtins":
                        self.params_type[name][key] = type_name
                    else:
                        self.params_type[name][key] = f"{module_name}.{type_name}"

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
        for proc in self.processes:

            name = proc["process"].__name__

            text_dependencies = ""
            if "require" in proc:
                for _, value in proc["require"].items():
                    if text_dependencies == "": text_dependencies += value
                    else: text_dependencies += ", "+value
            if text_dependencies == "": text_dependencies += "None"
            text_dependencies += "."

            text_inputs = ""
            if "input_params" in proc:
                for key, value in proc["input_params"].items():
                    type = self.params_type[name][key]
                    if text_inputs == "": text_inputs += f"{value} ({type})"
                    else: text_inputs += ", "+f"{value} ({type})"
            if "input_paths" in proc:
                for _, file in proc["input_paths"].items():
                    if text_inputs == "": text_inputs += file
                    else: text_inputs += ", "+file
            if text_inputs == "": text_inputs += "None"
            text_inputs += "."

            text_outputs = ""
            if "build" in proc:
                for _, build in proc["build"].items():
                    if text_outputs == "": text_outputs += build
                    else: text_outputs += ", "+build
            if text_outputs == "": text_outputs += "None"
            text_outputs += "."

            # Printing
            print("")
            print(
                colored(f"| {name} |", "magenta"),
            )
            print(
                colored(f"> Dependencies : {text_dependencies}", "blue"),
            )
            print(
                colored(f"> Inputs : {text_inputs}", "blue"),
            )
            print(
                colored(f"> Outputs : {text_outputs}", "blue"),
            )

    def init_studies(self):
        """Initialize studies"""

        # Open studies json file if existing
        if os.path.exists("studies.json"):
            with open("studies.json") as f:
                self.dict_studies = json.load(f)
        
        # Clean studies
        for study in list(self.dict_studies.keys()):
            if study not in self.studies:
                del self.dict_studies[study]
        
        # Clean input parameters
        for study in list(self.dict_studies.keys()):
            for param in list(self.dict_studies[study]["input_params"]):
                if param not in self.input_params:
                    del self.dict_studies[study]["input_params"][param]
        
        # Clean input paths
        for study in list(self.dict_studies.keys()):
            for file in list(self.dict_studies[study]["input_paths"]):
                if file not in self.input_paths:
                    del self.dict_studies[study]["input_paths"][file]
        
        # Initialize input parameters/paths
        for study in self.studies:
            
            if study not in self.dict_studies:
                self.dict_studies[study] = {
                    "execute": True,
                    "input_params": {},
                    "input_paths": {},
                }
            
            for param in self.input_params:
                if param not in self.dict_studies[study]["input_params"]:
                    if study == "Default":
                        self.dict_studies[study]["input_params"][param] = False
                    else:
                        self.dict_studies[study]["input_params"][param] = None
            
            for file in self.input_paths:
                if file not in self.dict_studies[study]["input_paths"]:
                    if study == "Default":
                        self.dict_studies[study]["input_paths"][file] = False
                    else:
                        self.dict_studies[study]["input_paths"][file] = None

        # Write studies json file
        with open("studies.json", "w") as f:
            json.dump(self.dict_studies, f, indent=4)

    def test_studies_modification(self):
        """Test if studies configurations have been modified"""

        # Loop over studies
        for study in self.studies:
            
            self.studies_modif[study] = False

            study_file = Path(study) / ".study.json"
            if study_file.exists():
                with open(study_file) as f:
                    dict_study = json.load(f)
                if self.dict_studies[study] != dict_study:
                    self.studies_modif[study] = True

    def test_studies_settings(self):
        """Check if studies has been properly configured"""
        
        # Loop over studies
        for study in self.studies:

            self.studies_messages[study] = []
            self.studies_config[study] = True

            for param in self.input_params:
                if self.dict_studies[study]["input_params"][param] is None:
                    self.studies_messages[study].append(f"(X) {param} not configured.")
                    self.studies_config[study] = False
                else:
                    if self.dict_studies[study]["input_params"][param]: text = "variable"
                    else: text = "fixed"
                    self.studies_messages[study].append(f"(V) {param} is {text}.")

            for file in self.input_paths:
                if self.dict_studies[study]["input_paths"][file] is None:
                    self.studies_messages[study].append(f"(X) {file} not configured.")
                    self.studies_config[study] = False
                else:
                    if self.dict_studies[study]["input_paths"][file]: text = "variable"
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
            if self.studies_modif[study]:
                print(
                    colored(f"(!) Configuration has been modified.", "yellow"),
                )
                self.clean_output_data(study)

            for message in self.studies_messages[study]:
                if "(V)" in message: print(colored(message, "green"))
                elif "(X)" in message: print(colored(message, "red"))
        
            if not self.studies_config[study]:
                print("")
                print(colored(f"(X) Please configure file :", "red"))
                print(colored(f"> {str(Path.cwd() / "studies.json")}", "red"))
                sys.exit()

    def init_process_settings(self):
        """Initialize process settings"""

        # Loop over studies
        for study in self.studies:

            # Open process json file if existing
            process_file = Path(study) / "process.json"
            if os.path.exists(process_file):
                with open(process_file) as f:
                    self.dict_process[study] = json.load(f)
            else:
                self.dict_process[study] = {}

            # Clean processes
            for process in list(self.dict_process[study].keys()):
                if process not in self.list_processes:
                    del self.dict_process[study][process]

            # Loop over processes
            for process in self.list_processes:
                if process not in self.dict_process[study]:
                    self.dict_process[study][process] = {
                        "execute": True,
                        "verbose": False,
                    }
            
            # Write studies json file
            with open(process_file, "w") as f:
                json.dump(self.dict_process[study], f, indent=4)

    def configure_inputs(self):
       """Configure inputs with lists of fixed/variable parameters/paths"""

       for study in self.studies:

            # Define list of fixed/variable parameters
            fixed_params = []
            variable_params = []
            for key, value in self.dict_studies[study]["input_params"].items():
                if value is True: variable_params.append(key)
                else: fixed_params.append(key)
            
            # Define list of fixed/variable paths
            fixed_paths = []
            variable_paths = []
            for key, value in self.dict_studies[study]["input_paths"].items():
                if value is True: variable_paths.append(key)
                else: fixed_paths.append(key)
            
            self.fixed_params[study] = fixed_params
            self.variable_params[study] = variable_params
            self.fixed_paths[study] = fixed_paths
            self.variable_paths[study] = variable_paths

    def init_data_tree(self):
        """Initialize data tree"""

        for study in self.studies:

            # Initialize study directory
            study_dir:Path = self.working_dir / study
            study_dir.mkdir(
                exist_ok=True,
                parents=True,
            )

            # Write study json if configuration has changed
            if self.studies_modif[study]:


                # Write new study json file
                with open(study_dir / ".study.json", "w") as f:
                    json.dump(self.dict_studies[study], f, indent=4)
            
            # Initialize inputs csv
            inputs_file:Path = study_dir / "inputs.csv"
            if (len(self.variable_params[study]) > 0) or \
               (len(self.variable_paths[study]) > 0):
                
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
            if len(self.input_paths) > 0:

                # Create inputs directory (if necessary)
                inputs_dir.mkdir(
                    exist_ok=True,
                    parents=True,
                )

                # Delete fixed paths (if necessary)
                inputs_files = [f for f in inputs_dir.iterdir() if f.is_file()]
                for file in inputs_files:
                    if os.path.split(file)[-1] not in self.fixed_paths[study]:
                        file.unlink()
                
                # Update inputs subfolders for variable paths
                if len(self.variable_paths[study]) > 0:

                    # Create subfolders (if necessary)    
                    for index in df_inputs.index:
                        
                        inputs_subfolder:Path = inputs_dir / index
                        inputs_subfolder.mkdir(
                            exist_ok=True,
                            parents=True,
                        )

                        # Delete variable paths (if necessary)
                        inputs_files = [f for f in inputs_subfolder.iterdir() if f.is_file()]
                        for file in inputs_files:
                            if os.path.split(file)[-1] not in self.variable_paths[study]:
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

    def clean_output_data(self,
        study: str,
    ):
        """Clean output data for a specific study"""

        # Initialize study directory
        study_dir:Path = self.working_dir / study

        # Outputs data
        outputs_folders = [f for f in study_dir.iterdir() if f.is_dir()]
        for folder in outputs_folders:
            if os.path.split(folder)[-1] != "0_inputs":
                shutil.rmtree(folder)

        # Paths file
        paths_file = study_dir / ".paths.json"
        if paths_file.exists(): paths_file.unlink()

    def set_inputs(self):
        """Set all inputs"""

        # Loop over studies
        for study in self.studies:

            # Define study directory
            study_dir:Path = self.working_dir / study
            
            # Go to study directory
            os.chdir(study_dir)

            # Initialize dictionary of input paths
            self.dict_input_paths[study] = {}

            # Fixed parameters 
            if len(self.fixed_params[study]) > 0:

                # Read json
                with open("inputs.json") as f:
                    self.dict_fixed_params[study] = json.load(f)
            
            else:
                self.dict_fixed_params[study] = {}

            # Fixed paths
            dict_input_paths = {}
            for file in self.fixed_paths[study]:
                dict_input_paths[file] = str(Path(os.getcwd()) / "0_inputs" / file)

            self.dict_input_paths[study] = {**self.dict_input_paths[study], **dict_input_paths}

            # Variable parameters
            if (len(self.variable_params[study]) > 0) or \
               (len(self.variable_paths[study]) > 0):
                
                # Read input dataframe
                self.dict_variable_params[study] = pd.read_csv(
                    filepath_or_buffer="inputs.csv",
                    index_col=0,
                )
            
            else:
                self.dict_variable_params[study] = pd.DataFrame()
            
            # Variable paths
            if len(self.variable_paths[study]) > 0:
                
                dict_input_paths = {}
                df_inputs = pd.read_csv(
                    filepath_or_buffer="inputs.csv",
                    index_col=0,
                )
                for file in self.variable_paths[study]:
                    dict_input_paths[file] = {}
                    for idx in df_inputs.index:
                        dict_input_paths[file][idx] = str(Path(os.getcwd()) / "0_inputs" / idx / file)

                self.dict_input_paths[study] = {**self.dict_input_paths[study], **dict_input_paths}

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
            self.fixed_paths_messages[study] = []
            self.fixed_params_config[study] = True
            self.fixed_paths_config[study] = True
            self.variable_params_messages[study] = {}
            self.variable_paths_messages[study] = {}
            self.variable_params_config[study] = {}
            self.variable_paths_config[study] = {}
            
            # Fixed parameters
            for param, value in self.dict_fixed_params[study].items():
                if value is None:
                    self.fixed_params_messages[study].append(f"(X) {param}")
                    self.fixed_params_config[study] = False
                else:
                    self.fixed_params_messages[study].append(f"(V) {param}")
            
            # Fixed paths
            for file in self.fixed_paths[study]:
                file_path:Path = Path("0_inputs") / file
                if not file_path.exists():
                    self.fixed_paths_messages[study].append(f"(X) {file}")
                    self.fixed_paths_config[study] = False
                else:
                    self.fixed_paths_messages[study].append(f"(V) {file}")

            # Variable inputs
            if (len(self.variable_params[study]) > 0) or \
               (len(self.variable_paths[study]) > 0):

                for index in self.dict_variable_params[study].index:

                    inputs_dir:Path = Path("0_inputs") / index

                    self.variable_params_messages[study][index] = []
                    self.variable_paths_messages[study][index] = []
                    self.variable_params_config[study][index] = True
                    self.variable_paths_config[study][index] = True
                    
                    # Variable parameters
                    for param in self.variable_params[study]:
                        value = self.dict_variable_params[study].at[index, param]
                        if pd.isna(value) or value == "":
                            self.variable_params_messages[study][index].append(f"(X) {param}")
                            self.variable_params_config[study][index] = False
                        else:
                            self.variable_params_messages[study][index].append(f"(V) {param}")

                    # Variable paths
                    for file in self.variable_paths[study]:
                        file_path:Path = inputs_dir / file
                        if not file_path.exists():
                            self.variable_paths_messages[study][index].append(f"(X) {file}")
                            self.variable_paths_config[study][index] = False
                        else:
                            self.variable_paths_messages[study][index].append(f"(V) {file}")
            
            # Go back to working directory
            os.chdir(self.working_dir) 

    def print_inputs(self):
        """Print inputs"""

        print("")
        print(
            colored("> INPUTS <", "blue", attrs=["reverse"]),
        )
        for study in self.studies:

            # Define study directory
            study_dir:Path = self.working_dir / study
            
            # Go to study directory
            os.chdir(study_dir)

            # Printing
            print("")
            print(colored(f"| {study} |", "magenta"))

            # ------------ #
            # Fixed inputs #
            # ------------ #
            list_text = [colored(f"> Common :", "blue")]
            list_errors = []
            config = True
            
            # Fixed parameters
            for message in self.fixed_params_messages[study]:
                if "(V)" in message:
                    list_text.append(colored(message, "green"))
                elif "(X)" in message:
                    list_text.append(colored(message, "red"))
                    if config:
                        list_errors.append(colored(f"> {str(Path.cwd() / "inputs.json")}", "red"))
                    config = False
            
            # Fixed paths
            for i, message in enumerate(self.fixed_paths_messages[study]):
                if "(V)" in message:
                    list_text.append(colored(message, "green"))
                elif "(X)" in message:
                    file = self.fixed_paths[study][i]
                    list_text.append(colored(message, "red"))
                    list_errors.append(colored(f"> {str(Path.cwd() / "0_inputs" / file)}", "red"))
            
            # Printing
            print(*list_text)

            if not self.fixed_params_config[study] or not self.fixed_paths_config[study]:
                print("")
                print(colored(f"(X) Please configure file(s) :", "red"))
                for error in list_errors:
                    print(error)
                sys.exit()
            
            # --------------- #
            # Variable inputs #
            # --------------- #
            list_errors = []
            config = True

            if (len(self.variable_params[study]) > 0) or \
               (len(self.variable_paths[study]) > 0):
                
                # Check if datasets have been defined
                if len(self.dict_variable_params[study].index) == 0:
                    print("")
                    print(colored(f"(X) Please define at least one dataset in file :", "red"))
                    print(colored(f"> {str(Path.cwd() / "inputs.csv")}", "red"))
                    sys.exit()

                for index in self.dict_variable_params[study].index:

                    list_text = [colored(f"> {index} :", "blue")]
                    
                    # Variable parameters
                    for message in self.variable_params_messages[study][index]:
                        if "(V)" in message:
                            list_text.append(colored(message, "green"))
                        elif "(X)" in message:
                            list_text.append(colored(message, "red"))
                            if config:
                                list_errors.append(colored(f"> {str(Path.cwd() / "inputs.csv")}", "red"))
                            config = False

                    # Variable paths
                    for i, message in enumerate(self.variable_paths_messages[study][index]):
                        if "(V)" in message:
                            list_text.append(colored(message, "green"))
                        elif "(X)" in message:
                            file = self.variable_paths[study][i]
                            list_text.append(colored(message, "red"))
                            list_errors.append(colored(f"> {str(Path.cwd() / "0_inputs" / index / file)}", "red"))

                    # Printing
                    print(*list_text)
        
                list_errors = sorted(list_errors, key=lambda x: '0_inputs' in x)
                if len(list_errors) > 0:
                    print("")
                    print(colored(f"(X) Please configure file(s) :", "red"))
                    for error in list_errors:
                        print(error)
                    sys.exit()

            # Go back to working directory
            os.chdir(self.working_dir) 

    def init_paths(self):
        """Initialize dictionary containing all paths"""

        # Loop over studies
        for study in self.studies:

            # Define study directory
            study_dir:Path = self.working_dir / study

            try:
                with open(study_dir / ".paths.json") as f:
                    dict_paths = json.load(f)
            except:
                dict_paths = {}
            
            self.dict_paths[study] = dict_paths

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
                
                if "hard_params" in proc: dict_hard_params = proc["hard_params"]
                else: dict_hard_params = {}
                if "input_params" in proc: input_params = proc["input_params"]
                else: input_params = {}
                if "input_paths" in proc: input_paths = proc["input_paths"]
                else: input_paths = {}
                if "require" in proc: require = proc["require"]
                else: require = {}
                if "build" in proc: build = proc["build"]
                else: build = {}

                # Define class object for the current process
                process = proc["process"]
                this_process:Process = process(
                    df_inputs=self.dict_variable_params[study],
                    dict_inputs=self.dict_fixed_params[study],
                    dict_input_paths=self.dict_input_paths[study],
                    dict_paths=self.dict_paths[study],
                    params=input_params,
                    paths=input_paths,
                    dict_hard_params=dict_hard_params,
                    fixed_params=self.fixed_params[study],
                    variable_params=self.variable_params[study],
                    fixed_paths=self.fixed_paths[study],
                    variable_paths=self.variable_paths[study],
                    require=require,
                    build=build,
                    is_processed=self.dict_process[study][self.list_processes[step]]["execute"],
                    verbose=self.dict_process[study][self.list_processes[step]]["verbose"],
                    diagram=self.diagram,
                )
                this_process.initialize()

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
                    "paths": this_process.paths,
                    "allpaths": this_process.allpaths,
                    "require": list(this_process.require.values()),
                    "build": list(this_process.build.values()),
                }

                # Update paths dictonary
                self.dict_paths[study] = this_process.dict_paths

                # Write paths json file
                with open(study_dir / ".paths.json", "w") as f:
                    json.dump(self.dict_paths[study], f, indent=4)

            # Go back to study directory
            os.chdir(study_dir)
            
            # Write diagram json file
            with open(".diagram.json", "w") as f:
                json.dump(self.diagram, f, indent=4)

            # # Write study json file
            # with open(".study.json", "w") as f:
            #     json.dump(self.dict_studies[study], f, indent=4)
        
        # Go back to working directory
        os.chdir(self.working_dir)