from __future__ import annotations

import os
import attrs
import json
from termcolor import colored

import numpy as np
import pandas as pd


@attrs.define
class Process():
    """Mother class of all classes of process."""

    name: str = attrs.field(default=None)
    df_inputs: pd.DataFrame = attrs.field(default=None)
    dict_inputs: dict = attrs.field(default=None)
    dict_input_paths: dict = attrs.field(default=None)
    dict_paths: dict = attrs.field(factory=dict)
    is_processed: bool = attrs.field(default=True)
    is_case: bool = attrs.field(default=True)
    params: list = attrs.field(factory=list)
    allparams: list = attrs.field(factory=list)
    paths: list = attrs.field(factory=list)
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
    dict_params: dict = attrs.field(default=None)
    dict_hard_params: dict = attrs.field(factory=dict)
    build: list = attrs.field(default=[])
    require: list = attrs.field(default=[])
    verbose: bool = attrs.field(default=True)
    index: str = attrs.field(default=None)
    diagram: dict = attrs.field(default={})
    from_inputs_json: bool = attrs.field(default=False)
    
    def __attrs_post_init__(self):

        if not self.from_inputs_json:
            
            self.variable_params_proc = [x for x in self.variable_params if x in self.params]
            self.fixed_params_proc = [x for x in self.fixed_params if x in self.params]
            self.fixed_paths_proc = [x for x in self.fixed_paths if x in self.paths]
            self.variable_paths_proc = [x for x in self.variable_paths if x in self.paths]

            # Define list with all parameters considering dependencies with previous processes
            self.allparams = self.params.copy()
            for require in self.require:
                for _, value in self.diagram.items():
                    if require in value.get("build"):
                        self.allparams = concat_lists_unique(
                            list1=self.params,
                            list2=value["allparams"],
                        )

            # Define list with all paths considering dependencies with previous processes
            self.allpaths = self.paths.copy()
            for require in self.require:
                for _, value in self.diagram.items():
                    if require in value.get("build"):
                        self.allpaths = concat_lists_unique(
                            list1=self.paths,
                            list2=value["allpaths"],
                        )

            if self.is_case:
                self.on_params_update()

    def __call__(self):

        # Update dictionary of parameters
        if not self.from_inputs_json:
            self.update_dict_params()

        for param, value in self.dict_params.items():
            setattr(self, param, value)

            # Printing
            print(colored(f"> {param} = {value}", "blue"))
        
        # Printing
        print(colored(">>> START", "green"))

    def on_params_update(self):

        # Create parameters dataframe and fill with variable parameters
        if (len(self.variable_params_proc) > 0) or (len(self.variable_paths_proc) > 0):
            self.df_params = self.df_inputs[self.variable_params_proc].copy()
        
        # There is no variable parameters / paths
        else:

            # Check parameters / paths dependencies
            variable_params = [x for x in self.variable_params if x in self.allparams]
            variable_paths = [x for x in self.variable_paths if x in self.paths]
            
            # There are variable parameters / paths from previous process
            if (len(variable_params) > 0) or (len(variable_paths) > 0):
                self.df_params = pd.DataFrame(self.df_inputs.index, columns=["ID"]).set_index("ID")
            # There is no variable parameter from previous process
            else:
                self.is_case = False
        
        # Add fixed parameters to the dataframe
        if self.is_case:
            for param in self.fixed_params_proc:
                self.df_params[param] = self.dict_inputs[param]
    
    def update_dict_params(self):

        # Add inputs parameters
        if self.is_case:

            self.dict_params = {}
            for param in self.df_params.columns:
                value = convert_value(self.df_params.at[self.index, param])
                self.dict_params[param] = value
            if self.df_inputs.loc[self.index, "EXECUTE"] == 0:
                self.is_processed = False
        else:

            self.dict_params = {param: self.dict_inputs[param] for param in self.fixed_params_proc}
        
        # Add hard parameters
        for param, value in self.dict_hard_params.items():
            self.dict_params[param] = value

        # Add input paths
        for file in self.fixed_paths_proc:
            key = os.path.splitext(file)[0]
            self.dict_params[key] = self.dict_input_paths[key]
        for file in self.variable_paths_proc:
            key = os.path.splitext(file)[0]
            self.dict_params[key] = self.dict_input_paths[key][self.index]
        
        # Add previous outputs
        for output in self.require:
            output_path = self.get_build_path(output)
            self.dict_params[output] = output_path

        # Write json file containing all parameters
        with open("parameters.json", "w") as f:
            json.dump(self.dict_params, f, indent=4)

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

        print(colored("COMPLETED <<<", "green"))


def convert_value(value):
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


def concat_lists_unique(
    list1: list,
    list2: list,
):
    return list(dict.fromkeys(list1 + list2))