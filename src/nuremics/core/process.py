from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Callable

import attrs
import pandas as pd
from termcolor import colored

from .utils import (
    concat_lists_unique,
    convert_value,
)


@attrs.define
class Process:
    """Mother class of all classes of process."""

    name: str = attrs.field(default=None)
    study: str = attrs.field(default=None)
    df_user_params: pd.DataFrame = attrs.field(default=None)
    dict_user_params: dict = attrs.field(default=None)
    dict_user_paths: dict = attrs.field(default=None)
    dict_paths: dict = attrs.field(factory=dict)
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
    output_paths: dict = attrs.field(factory=dict)
    overall_analysis: dict = attrs.field(factory=dict)
    dict_analysis: dict = attrs.field(factory=dict)
    required_paths: dict = attrs.field(factory=dict)
    silent: bool = attrs.field(default=False)
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
        for required_paths in list(self.required_paths.values()):
            for _, value in self.diagram.items():
                if required_paths in value.get("output_paths"):
                    self.allparams = concat_lists_unique(
                        list1=list(self.params.values()),
                        list2=value["allparams"],
                    )

        # Define list with all paths considering dependencies with previous processes
        self.allpaths = list(self.paths.values()).copy()
        for required_path in list(self.required_paths.values()):
            for _, value in self.diagram.items():
                if required_path in value.get("output_paths"):
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
            variable_paths = [x for x in self.variable_paths if x in self.allpaths]

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

        # Add previous output paths
        for key, value in self.required_paths.items():
            output_path = self.get_output_path(value)
            self.dict_inputs[key] = output_path

        # Add output analysis
        for out, value in self.overall_analysis.items():
            self.dict_inputs[out] = value

        # Add output paths
        for out, value in self.output_paths.items():
            self.dict_inputs[out] = value

        # Write json file containing all parameters
        with open("inputs.json", "w") as f:
            json.dump(self.dict_inputs, f, indent=4)

    def get_output_path(self,
        output_path: str,
    ):
        """Function to get the path to an output within the paths dictionary"""
        # Initialize path to return
        path = None

        if isinstance(self.dict_paths[output_path], dict):
            for key, value in self.dict_paths[output_path].items():
                if key == self.index:
                    path = value
        else:
            path = self.dict_paths[output_path]


        if not Path(path).exists():

            # Printing
            print()
            print(colored(f"(X) Required {output_path} is missing :", "red"))
            print(colored("> Please execute the necessary previous process that will build it.", "red"))

            sys.exit(1)

        return path

    def update_output(self,
        output_path: str,
        dump: str,
    ):
        if output_path not in self.dict_paths:
            self.dict_paths[output_path] = None

        if self.is_case:
            if self.dict_paths[output_path] is None: self.dict_paths[output_path] = {}
            self.dict_paths[output_path][self.index] = os.path.join(os.getcwd(), dump)
        else:
            self.dict_paths[output_path] = os.path.join(os.getcwd(), dump)

    @staticmethod
    def analysis_function(
        func: Callable,
    ) -> Callable:

        func._is_analysis = True
        return func

    def process_output(self,
        out: str,
        func: Callable[..., None],
        **kwargs,
    ):
        if not getattr(func, "_is_analysis", False):
            print(colored(f'(X) Function "{func.__name__}" is not a valid analysis function.', "red"))
            sys.exit(1)

        output = self.dict_paths[out]
        analysis = self.dict_analysis[self.name]
        if isinstance(output, dict):
            func(output, analysis, **kwargs)

    def finalize(self):

        for _, value in self.output_paths.items():
            self.update_output(
                output_path=value,
                dump=value,
            )

        print(colored("COMPLETED <<<", "green"))
