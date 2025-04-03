from __future__ import annotations

import os
import attrs

import numpy as np
import pandas as pd


@attrs.define
class Process():
    """Mother class of all classes of process."""

    name: str = attrs.field(default=None)
    df_inputs: pd.DataFrame = attrs.field(default=None)
    dict_paths: dict = attrs.field(factory=dict)
    is_processed: bool = attrs.field(default=True)
    is_case: bool = attrs.field(default=True)
    user_params: list = attrs.field(factory=list)
    params: list = attrs.field(factory=list)
    df_params: pd.DataFrame = attrs.field(default=None)
    dict_params: dict = attrs.field(factory=dict)
    dict_fixed_params: dict = attrs.field(factory=dict)
    build: list = attrs.field(factory=list)
    require: list = attrs.field(default=[])
    verbose: bool = attrs.field(default=True)
    index: str = attrs.field(default=None)
    erase: bool = attrs.field(default=False)

    def __attrs_post_init__(self):

        self.user_params = self.params.copy()

        if self.is_case:
            self.on_params_update()

    def __call__(self):

        for param in self.user_params:
            setattr(self, param, self.dict_params[param])
        for param in self.dict_fixed_params.keys():
            setattr(self, param, self.dict_fixed_params[param])
        
        for output in self.require:
            setattr(self, output, self.get_build_path(output))

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

        if self.df_inputs.loc[self.index, "EXECUTE"] == 0:
            self.is_processed = False

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