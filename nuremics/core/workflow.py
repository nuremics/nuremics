from __future__ import annotations

import os
import sys
import attrs
from tkinter import filedialog
from tkinter import *

import json
import numpy as np
import pandas as pd
import importlib
import jinja2
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from multiprocessing import Process, Pipe

from pylatex import Document, Section, Package, NoEscape
from pylatex.base_classes.containers import Fragment

class WorkFlow:
    """Manage workflow of processes."""
    
    def __init__(
        self,
        working_dir: Path,
        app_name: str,
        processes: list,
        generate_report: bool = True,
        verbose: bool = True,
    ):
        """Initialization."""
        
        # -------------------- #
        # Initialize variables #
        # -------------------- #
        self.app_name = app_name
        self.processes = processes
        self.diagram = {}
        self.generate_report = generate_report
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
        
        # ------------------------ #
        # Create INCLUDE directory #
        # ------------------------ #
        Path("INCLUDE").mkdir(exist_ok=True, parents=True)
        
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

        # --------------------------- #
        # Initialize pylatex document #
        # --------------------------- #
        self.doc = Document()
        self.doc.packages.append(Package("amsmath"))
        self.doc.packages.append(Package("float"))
        self.doc.preamble.append(NoEscape(r"\graphicspath{{./INCLUDE/}}"))

    def __call__(self):
        """Launch workflow of processes."""
        
        # --------------- #
        # Launch workflow #
        # --------------- #
        for step, process in enumerate(self.processes):

            if not process["execute"]:
                continue
            
            # Define class object for the current process
            module = process["module"]
            if "fixedParams" in process:
                dict_fixed_params = process["fixedParams"]
            else:
                dict_fixed_params = {}
            
            this_process:AllProcesses = module(
                df_inputs=self.df_inputs,
                dict_paths=self.dict_paths,
                params=process["userParams"],
                dict_fixed_params=dict_fixed_params,
                verbose=process["verbose"],
                include_dir=Path(os.getcwd()) / "INCLUDE",
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
                            this_process.params = self.concat_lists_unique(
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
                        print(" > WARNING : Process is skipped !")
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
                    print(" > WARNING : Process is skipped !")
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

    def convert_value(self, value):
        """Function to convert values in python native types"""

        if value == "NA":
            return None
        elif isinstance(value, (bool, np.bool_)):
            return bool(value)
        elif isinstance(value, (int, np.int64)):
            return int(value)
        elif isinstance(value, (float, np.float64)):
            return float(value)
        elif isinstance(value, str):
            return str(value)
        else:
            return value

    def concat_lists_unique(self,
        list1: list,
        list2: list,
    ):
        return list(dict.fromkeys(list1 + list2))


@attrs.define
class AllProcesses():
    """Mother class of all classes of processes."""

    name: str = attrs.field(default=None)
    df_inputs: pd.DataFrame = attrs.field(default=None)
    dict_paths: dict = attrs.field(factory=dict)
    include_dir: Path = attrs.field(default=None)
    kwargs: dict = attrs.field(factory=dict)
    is_processed: bool = attrs.field(default=True)
    is_case: bool = attrs.field(default=True)
    user_params: list = attrs.field(factory=list)
    params: list = attrs.field(factory=list)
    df_params: pd.DataFrame = attrs.field(default=None)
    dict_params: dict = attrs.field(factory=dict)
    dict_fixed_params: dict = attrs.field(factory=dict)
    build: list = attrs.field(factory=list)
    require: list = attrs.field(default=None)
    verbose: bool = attrs.field(default=True)
    index: str = attrs.field(default=None)

    def __attrs_post_init__(self):

        self.user_params = self.params.copy()

        if self.is_case:
            self.on_params_update()

    def on_params_update(self):

        df = self.df_inputs.reset_index().groupby(self.params)["ID"].agg(list).reset_index(name="ID")
        df["ID"] = df["ID"].apply(lambda x: "_".join(x))
        self.df_params = df.set_index("ID")
    
    def update_dict_params(self):

        # Printing
        print("")
        print(f"> Processing {self.index} with set of parameters :")

        self.dict_params = {}
        for param in self.df_params.columns:
            value = self.convert_value(self.df_params.at[self.index, param])
            self.dict_params[param] = value
            
            # Printing
            print(f"|--> {param} = {value}")
        
        # Printing
        print("")

    def convert_value(self, value):
        """Function to convert values in python native types"""

        if value == "NA":
            return None
        elif isinstance(value, (bool, np.bool_)):
            return bool(value)
        elif isinstance(value, (int, np.int64)):
            return int(value)
        elif isinstance(value, (float, np.float64)):
            return float(value)
        elif isinstance(value, str):
            return str(value)
        else:
            return value

    def get_build_path(self,
        build: str,
    ):
        """Function to get the path to a build within the paths dictionary"""
        
        # Initialize path to return
        path = None

        for key, value in self.dict_paths[build].items():

            # Split key into list
            key_parts = key.split("_")
            # Split index into list
            index_parts = self.index.split("_")
            
            # Verify that index is in the key 
            if all(term in key_parts for term in index_parts):
                path = value
            
        return path

    @classmethod
    def builder(cls, build=None):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                
                # Add build entity if not existing
                if build not in self.build:
                    self.build.append(build)

                # Execute check function
                is_stopped = self.check(build)

                # if is_stopped:
                #     # Printing
                #     print(f"> WARNING : [{build}] is already built !")
                #     return
                
                # Call decorated function
                result = func(self, *args, **kwargs)
                
                # Get dump from args or kwargs
                if args:
                    dump = args[0]  # First argument is taken in args list
                elif kwargs:
                    first_key = next(iter(kwargs))  # First key is taken in kwargs dictionary
                    dump = kwargs[first_key]  # Get dump value
                else:
                    dump = None
                
                # Execute update function if build is defined and dump is found
                if build is not None and dump is not None:
                    self.update(build, dump)
                
                return result
            return wrapper
        return decorator

    def check(self,
        build: str,
    ):
        is_stopped = False
        if self.is_case:
            if (build in self.dict_paths) and (self.index in self.dict_paths[build]):
                is_stopped = True
        else:
            if (build in self.dict_paths):
                is_stopped = True
        
        return is_stopped

    def update(self,
        build: str,
        dump: str,
    ):

        if build not in self.dict_paths:
            self.dict_paths[build] = {}

        if self.is_case:
            self.dict_paths[build][self.index] = os.path.join(os.getcwd(), dump)
        else:
            self.dict_paths[build] = os.path.join(os.getcwd(), dump)