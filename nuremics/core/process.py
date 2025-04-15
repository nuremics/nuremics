from __future__ import annotations

import os
import attrs
import json

import numpy as np
import pandas as pd


@attrs.define
class Process():
    """Mother class of all classes of process."""

    name: str = attrs.field(default=None)
    df_inputs: pd.DataFrame = attrs.field(default=None)
    dict_inputs: dict = attrs.field(default=None)
    dict_paths: dict = attrs.field(factory=dict)
    is_processed: bool = attrs.field(default=True)
    is_case: bool = attrs.field(default=True)
    params: list = attrs.field(factory=list)
    allparams: list = attrs.field(factory=list)
    variable_params: list = attrs.field(factory=list)
    fixed_params: list = attrs.field(factory=list)
    df_params: pd.DataFrame = attrs.field(default=None)
    dict_params: dict = attrs.field(factory=dict)
    dict_hard_params: dict = attrs.field(factory=dict)
    dict_out_to_in: dict = attrs.field(default={})
    build: list = attrs.field(factory=list)
    require: list = attrs.field(default=[])
    verbose: bool = attrs.field(default=True)
    index: str = attrs.field(default=None)
    erase: bool = attrs.field(default=False)
    diagram: dict = attrs.field(default={})

    def __attrs_post_init__(self):

        self.variable_params = list(
            set(self.df_inputs.columns) & 
            set(self.params)
        )
        self.fixed_params = list(
            set(list(self.dict_inputs.keys())) & 
            set(self.params)
        )
    
    def init_params(self):

        # Define list with all parameters considering dependencies with previous processes
        self.allparams = self.params.copy()
        for require in self.require:
            for _, value in self.diagram.items():
                if require in value.get("build"):
                    self.allparams = concat_lists_unique(
                        list1=self.params,
                        list2=value["allparams"],
                    )

        if self.is_case:
            self.on_params_update()

    def __call__(self):

        for output in self.require:
            output_path = self.get_build_path(output)
            setattr(self, output, output_path)
            self.dict_out_to_in[output] = output_path

        # Update dictionary of parameters
        self.update_dict_params()

        for param in self.params:
            setattr(self, param, self.dict_params[param])
        for param in self.dict_hard_params.keys():
            setattr(self, param, self.dict_hard_params[param])

    def on_params_update(self):

        # Create parameters dataframe and fill with variable parameters
        if len(self.variable_params) > 0:
            self.df_params = self.df_inputs[self.variable_params].copy()
        else:
            # Check parameters dependencies
            variable_params = list(
                set(self.df_inputs.columns) & 
                set(self.allparams)
            )
            if len(variable_params) == 0:
                self.is_case = False
            else:
                self.df_params = pd.DataFrame(self.df_inputs.index, columns=["ID"]).set_index("ID")
        
        # Add fixed parameters to the dataframe
        if self.is_case:
            for param in self.fixed_params:
                self.df_params[param] = self.dict_inputs[param]
    
    def update_dict_params(self):

        if self.is_case:

            # Printing
            print("")
            print(f"> Processing {self.index} with inputs :")

            self.dict_params = {}
            for param in self.df_params.columns:
                value = convert_value(self.df_params.at[self.index, param])
                self.dict_params[param] = value
                
                # Printing
                print(f"|--> {param} = {value}")
            
            if self.df_inputs.loc[self.index, "EXECUTE"] == 0:
                self.is_processed = False
        
        else:

            # Printing
            print("")
            print(f"> Processing inputs :")

            self.dict_params = {param: self.dict_inputs[param] for param in self.fixed_params}
            for param, value in self.dict_params.items():

                # Printing
                print(f"|--> {param} = {value}")
        
        for out, path in self.dict_out_to_in.items():

                # Printing
                print(f"|--> {out} = {path}")
        
        # Printing
        print("")
        print(">>>>>>>>>>>>>>>>>>>>>>>>> START <<<<<<<<<<<<<<<<<<<<<<<<<")

        # Write json file containing current parameters
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

    @classmethod
    def builder(cls, build=None):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                
                # Add build entity if not existing
                if build not in self.build:
                    self.build.append(build)

                # Execute check function
                is_stopped = self.check(build)

                if is_stopped and not self.erase:
                    # Printing
                    print(f"> WARNING : [{build}] is already built !")
                    return
                
                # Call decorated function
                result = func(self, *args, **kwargs)
                
                # Get dump from args or kwargs
                if args:
                    # First argument is taken in args list
                    dump = args[0]
                
                elif kwargs:
                    # First key is taken in kwargs dictionary
                    first_key = next(iter(kwargs)) 
                    # Get dump value
                    dump = kwargs[first_key]
                
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

    def finalize(self):

        print(">>>>>>>>>>>>>>>>>>>>>>> COMPLETED <<<<<<<<<<<<<<<<<<<<<<<")


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