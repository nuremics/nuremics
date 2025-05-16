from __future__ import annotations

import os
import attrs
import json
from termcolor import colored

import pandas as pd

from .utils import (
    convert_value,
    concat_lists_unique,
)


@attrs.define
class Process():
    """Mother class of all classes of process."""

    name: str = attrs.field(default=None)
    df_user_params: pd.DataFrame = attrs.field(default=None)
    dict_user_params: dict = attrs.field(default=None)
    dict_user_paths: dict = attrs.field(default=None)
    dict_paths: dict = attrs.field(factory=dict)
    is_processed: bool = attrs.field(default=True)
    is_case: bool = attrs.field(default=True)
    params: dict = attrs.field(factory=dict)
    allparams: list = attrs.field(factory=list)
    paths: dict = attrs.field(factory=dict)
    allpaths: list = attrs.field(factory=list)
    fixed_params: list = attrs.field(default=None)
    variable_params: list = attrs.field(default=None)
    fixed_paths: list = attrs.field(default=None)
    variable_paths: list = attrs.field(default=None)
    fixed_params_proc: list = attrs.field(factory=list)
    variable_params_proc: list = attrs.field(factory=list)
    fixed_paths_proc: list = attrs.field(factory=list)
    variable_paths_proc: list = attrs.field(factory=list)
    df_params: pd.DataFrame = attrs.field(default=None)
    dict_inputs: dict = attrs.field(default=None)
    dict_hard_params: dict = attrs.field(factory=dict)
    build: dict = attrs.field(default={})
    require: dict = attrs.field(default={})
    verbose: bool = attrs.field(default=True)
    index: str = attrs.field(default=None)
    diagram: dict = attrs.field(default={})
    set_inputs: bool = attrs.field(default=False)
    
    def initialize(self):
            
        self.variable_params_proc = [x for x in self.variable_params if x in list(self.params.values())]
        self.fixed_params_proc = [x for x in self.fixed_params if x in list(self.params.values())]
        self.fixed_paths_proc = [x for x in self.fixed_paths if x in list(self.paths.values())]
        self.variable_paths_proc = [x for x in self.variable_paths if x in list(self.paths.values())]

        # Define list with all parameters considering dependencies with previous processes
        self.allparams = list(self.params.values()).copy()
        for require in list(self.require.values()):
            for _, value in self.diagram.items():
                if require in value.get("build"):
                    self.allparams = concat_lists_unique(
                        list1=list(self.params.values()),
                        list2=value["allparams"],
                    )

        # Define list with all paths considering dependencies with previous processes
        self.allpaths = list(self.paths.values()).copy()
        for require in list(self.require.values()):
            for _, value in self.diagram.items():
                if require in value.get("build"):
                    self.allpaths = concat_lists_unique(
                        list1=list(self.paths.values()),
                        list2=value["allpaths"],
                    )

        if self.is_case:
            self.on_params_update()

    def __call__(self):

        # Update dictionary of parameters
        if not self.set_inputs:
            self.update_dict_inputs()

        for param, value in self.dict_inputs.items():
            setattr(self, param, value)

            # Printing
            print(colored(f"> {param} = {value}", "blue"))
        
        # Printing
        print(colored(">>> START", "green"))

    def on_params_update(self):

        # Create parameters dataframe and fill with variable parameters
        if (len(self.variable_params_proc) > 0) or (len(self.variable_paths_proc) > 0):
            self.df_params = self.df_user_params[self.variable_params_proc].copy()
        
        # There is no variable parameters / paths
        else:

            # Check parameters / paths dependencies
            variable_params = [x for x in self.variable_params if x in self.allparams]
            variable_paths = [x for x in self.variable_paths if x in self.paths]
            
            # There are variable parameters / paths from previous process
            if (len(variable_params) > 0) or (len(variable_paths) > 0):
                self.df_params = pd.DataFrame(self.df_user_params.index, columns=["ID"]).set_index("ID")
            # There is no variable parameter from previous process
            else:
                self.is_case = False
        
        # Add fixed parameters to the dataframe
        if self.is_case:
            for param in self.fixed_params_proc:
                self.df_params[param] = self.dict_user_params[param]
    
    def update_dict_inputs(self):

        # Add user parameters
        if self.is_case:

            self.dict_inputs = {}
            params_inv = {v: k for k, v in self.params.items()}
            for param in self.df_params.columns:
                value = convert_value(self.df_params.at[self.index, param])
                self.dict_inputs[params_inv[param]] = value
            if self.df_user_params.loc[self.index, "EXECUTE"] == 0:
                self.is_processed = False
        else:
            self.dict_inputs = {k: self.dict_user_params[v] for k, v in self.params.items()}
        
        # Add hard parameters
        for param, value in self.dict_hard_params.items():
            self.dict_inputs[param] = value

        # Add user paths
        paths_inv = {v: k for k, v in self.paths.items()}
        for file in self.fixed_paths_proc:
            self.dict_inputs[paths_inv[file]] = self.dict_user_paths[file]
        for file in self.variable_paths_proc:
            self.dict_inputs[paths_inv[file]] = self.dict_user_paths[file][self.index]
        
        # Add previous outputs
        for key, value in self.require.items():
            output_path = self.get_build_path(value)
            self.dict_inputs[key] = output_path

        # Write json file containing all parameters
        with open("inputs.json", "w") as f:
            json.dump(self.dict_inputs, f, indent=4)

    def get_build_path(self,
        build: str,
    ):
        """Function to get the path to a build within the paths dictionary"""
        
        # Initialize path to return
        path = None

        if isinstance(self.dict_paths[build], dict):
            for key, value in self.dict_paths[build].items():
                if key == self.index:
                    path = value
        else:
            path = self.dict_paths[build]

        return path

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

    def finalize(self):

        for _, value in self.build.items():
            self.update(
                build=value,
                dump=value,
            )

        print(colored("COMPLETED <<<", "green"))