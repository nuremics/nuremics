from __future__ import annotations

import os
import pathlib
import sys

import json
import shutil
import numpy as np
import pandas as pd
from pathlib import Path
from termcolor import colored

from .process import Process
from .utils import (
    get_self_method_calls,
    only_function_calls,
    extract_inputs_and_types,
    extract_analysis,
    extract_self_output_keys,
)
from importlib.resources import files


class WorkFlow:
    """Manage workflow of processes."""

    def __init__(
        self,
        app_name: str,
        config_path: Path,
        workflow: list,
        silent: bool = False,
    ):
        """Initialization."""

        # -------------------- #
        # Initialize variables #
        # -------------------- #
        self.app_name = app_name
        self.config_path = config_path
        self.list_workflow = workflow
        self.list_processes = []
        self.dict_inputs = {}
        self.dict_datasets = {}
        self.dict_studies = {}
        self.dict_process = {}
        self.dict_analysis = {}
        self.user_params = []
        self.user_paths = []
        self.output_paths = []
        self.overall_analysis = []
        self.analysis_settings = {}
        self.params_type = {}
        self.operations_by_process = {}
        self.inputs_by_process = {}
        self.params_by_process = {}
        self.paths_by_process = {}
        self.outputs_by_process = {}
        self.analysis_by_process = {}
        self.settings_by_process = {}
        self.params_plug = {}
        self.paths_plug = {}
        self.outputs_plug = {}
        self.analysis_plug = {}
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
        self.dict_user_paths = {}
        self.dict_paths = {}
        self.diagram = {}
        self.silent = silent

        # ------------------------------------ #
        # Define and create nuremics directory #
        # ------------------------------------ #
        self.config_path.mkdir(
            exist_ok=True,
            parents=True,
        )

        # -------------------- #
        # Create settings file #
        # -------------------- #
        settings_file = self.config_path / "settings.json"
        if not settings_file.exists():
            dict_settings = {
                "default_working_dir": None,
                "apps": {},
            }
            with open(settings_file, "w") as f:
                json.dump(dict_settings, f, indent=4)
        
        # -------------------------- #
        # Define settings dictionary #
        # -------------------------- #
        with open(settings_file) as f:
            self.dict_settings = json.load(f)
        
        # ------------------------------- #
        # Initialize application settings #
        # ------------------------------- #
        if self.app_name not in self.dict_settings["apps"]:
            self.dict_settings["apps"][self.app_name] = {
                "working_dir": None,
            }

        # ----------------------------- #
        # Set default working directory #
        # ----------------------------- #
        if self.dict_settings["default_working_dir"] is None:
            for _, value in self.dict_settings["apps"].items():
                if value["working_dir"] is not None:
                    self.dict_settings["default_working_dir"] = value["working_dir"]
                    break

        # ------------------- #
        # Write settings file #
        # ------------------- #
        with open(settings_file, "w") as f:
            json.dump(self.dict_settings, f, indent=4)

        # ------------------------ #
        # Define list of processes #
        # ------------------------ #
        for proc in self.list_workflow:
            self.list_processes.append(proc["process"].__name__)

    def print_logo(self):
        """Print ASCII NUREMICS logo"""

        ascii_logo_path:str = files("nuremics.resources").joinpath("logo.txt")
        f = open(ascii_logo_path, "r")
        for line in f:
            lines = f.readlines()
        print()
        for line in lines:
            print(colored(line.rstrip(), "yellow"))

    def print_application(self):
        """Print application"""

        # Printing
        print()
        print(
            colored("> APPLICATION <", "blue", attrs=["reverse"]),
        )
        print()
        print(
            colored(f"| Workflow |", "magenta"),
        )
        print(
            colored(f"{self.app_name}_____", "blue"),
        )

        # Define number of spaces taken by the workflow print
        nb_spaces_app = len(self.app_name)+5

        # Print diagram of processes and operations
        error = False
        for i, proc in enumerate(self.list_workflow):

            proc_name = proc["process"].__name__
            process = proc["process"]
            this_process:Process = process()

            # Define number of spaces taken by the application print
            nb_spaces_proc = len(proc_name)+10

            # Get list of operations for current process
            self.operations_by_process[proc_name] = get_self_method_calls(this_process.__class__)

            # Test if process call contains only call to operations
            valid_call = only_function_calls(
                method=this_process.__call__,
                allowed_methods=self.operations_by_process[proc_name]
            )

            # Printing
            if valid_call:
                print(
                    colored(" "*nb_spaces_app+f"|_____{proc_name}_____", "blue"),
                )
                for op_name in self.operations_by_process[proc_name]:

                    if i < len(self.list_workflow)-1:
                        text = " "*nb_spaces_app+"|"+" "*nb_spaces_proc+f"|_____{op_name}"
                    else:
                        text = " "*(nb_spaces_app+1)+" "*nb_spaces_proc+f"|_____{op_name}"

                    # Printing
                    print(
                        colored(text, "blue"),
                    )
            else:
                print(
                    colored(" "*nb_spaces_app+f"|_____{proc_name}_____", "blue") + \
                    colored("(X)", "red")
                )
                error = True

            if i < len(self.list_workflow)-1:
                print(
                    colored(" "*nb_spaces_app+"|", "blue"),
                )

        if error:
            print()
            print(colored(f"(X) Each process must only call its internal function(s):", "red"))
            print()
            print(colored(f"    def __call__(self):", "red"))
            print(colored(f"        super().__call__()", "red"))
            print()
            print(colored(f"        self.operation1()", "red"))
            print(colored(f"        self.operation2()", "red"))
            print(colored(f"        self.operation3()", "red"))
            print(colored(f"        ...", "red"))
            sys.exit(1)

    def set_working_directory(self):
        """Set working directory"""
        
        # --------------------- #
        # Set working directory #
        # --------------------- #
        settings_file = self.config_path / "settings.json"
        if self.dict_settings["apps"][self.app_name]["working_dir"] is None:
            print()
            print(colored(f'(X) Please define {self.app_name} "working_dir" in file :', "red"))
            print(colored(f"> {str(settings_file)}", "red"))
            sys.exit(1)
            # if self.dict_settings["default_working_dir"] is None:
            #     print()
            #     print(colored(f'(X) Please define {self.app_name} "working_dir" in file :', "red"))
            #     print(colored(f"> {str(settings_file)}", "red"))
            #     sys.exit(1)
            # else:
            #     print()
            #     print(colored(f'(!) Found "default_working_dir": {self.dict_settings["default_working_dir"]}', "yellow"))
            #     while True:
            #         answer = input(colored(f'Accept it as "working_dir" for {self.app_name}: [Y/n] ', "yellow")).strip().lower()
            #         if answer in ["y", "yes", ""]:
            #             self.dict_settings["apps"][self.app_name]["working_dir"] = self.dict_settings["default_working_dir"]
            #             break
            #         elif answer in ["n", "no"]:
            #             print()
            #             print(colored(f'(X) Please define {self.app_name} "working_dir" in file :', "red"))
            #             print(colored(f"> {str(settings_file)}", "red"))
            #             sys.exit(1)
        
        self.working_dir = Path(self.dict_settings["apps"][self.app_name]["working_dir"]) / self.app_name
        
        # ------------------- #
        # Write settings file #
        # ------------------- #
        with open(settings_file, "w") as f:
            json.dump(self.dict_settings, f, indent=4)

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

    def get_inputs(self):
        """Get inputs"""

        for proc in self.list_workflow:

            process = proc["process"]
            name = proc["process"].__name__
            this_process:Process = process()

            self.inputs_by_process[name] = extract_inputs_and_types(this_process)
            self.analysis_by_process[name], self.settings_by_process[name] = extract_analysis(this_process)

            self.params_by_process[name] = {}
            self.paths_by_process[name] = []
            self.params_plug[name] = {}
            self.paths_plug[name] = {}
            self.analysis_plug[name] = {}

            for key, value_type in self.inputs_by_process[name].items():

                # Get the module and type name
                module_name = value_type.__module__
                type_name = value_type.__name__

                if module_name == "builtins":
                    type = type_name
                else:
                    type = f"{module_name}.{type_name}"

                if key not in self.analysis_by_process[name]:

                    if issubclass(value_type, pathlib.Path):
                        self.paths_by_process[name].append(key)
                        if ("user_paths" in proc) and (key in proc["user_paths"]):
                            self.paths_plug[name][key] = [proc["user_paths"][key], "user_paths"]
                        elif ("required_paths" in proc) and (key in proc["required_paths"]):
                            self.paths_plug[name][key] = [proc["required_paths"][key], "required_paths"]
                        else:
                            self.paths_plug[name][key] = None

                    else:
                        self.params_by_process[name][key] = [value_type, type]
                        if ("user_params" in proc) and (key in proc["user_params"]):
                            self.params_plug[name][key] = [proc["user_params"][key], "user_params"]
                        elif ("hard_params" in proc) and (key in proc["hard_params"]):
                            self.params_plug[name][key] = [proc["hard_params"][key], "hard_params"]
                        else:
                            self.params_plug[name][key] = None

                else:
                    if ("overall_analysis" in proc) and (key in proc["overall_analysis"]):
                        self.analysis_plug[name][key] = proc["overall_analysis"][key]
                    else:
                        self.analysis_plug[name][key] = None

    def get_outputs(self):
        """Get outputs"""

        for proc in self.list_workflow:

            process = proc["process"]
            name = proc["process"].__name__
            this_process:Process = process()

            self.outputs_by_process[name] = []
            self.outputs_plug[name] = {}

            for op in self.operations_by_process[name]:
                output_paths = extract_self_output_keys(getattr(this_process, op))
                for output_path in output_paths:
                    if output_path not in self.outputs_by_process[name]:
                        self.outputs_by_process[name].append(output_path)

            for output in self.outputs_by_process[name]:
                if ("output_paths" in proc) and (output in proc["output_paths"]):
                    self.outputs_plug[name][output] = proc["output_paths"][output]
                else:
                    self.outputs_plug[name][output] = None

    def init_config(self):
        """Initialize configuration"""

        for _, process in enumerate(self.list_workflow):

            name = process["process"].__name__

            # Define list of user parameters
            if "user_params" in process:
                for key, value in process["user_params"].items():
                    if key in self.params_by_process[name]:
                        self.user_params.append(value)
                    else:
                        print()
                        print(colored(f'(X) {key} defined in "user_params" is not an input parameter of {name}.', "red"))
                        sys.exit(1)

            # Check on hard parameters
            if "hard_params" in process:
                for key, _ in process["hard_params"].items():
                    if key not in self.params_by_process[name]:
                        print()
                        print(colored(f'(X) {key} defined in "hard_params" is not an input parameter of {name}.', "red"))
                        sys.exit(1)

            # Define list of user paths
            if "user_paths" in process:
                for key, value in process["user_paths"].items():
                    if key in self.paths_by_process[name]:
                        self.user_paths.append(value)
                    else:
                        print()
                        print(colored(f"(X) {key} is not an input path of {name}.", "red"))
                        sys.exit(1)

            # Check on required paths
            if "required_paths" in process:
                for _, value in process["required_paths"].items():
                    if value not in self.output_paths:
                        print()
                        print(colored(f'(X) {value} defined in {name} "required_paths" must be defined in previous process "output_paths".', "red"))
                        sys.exit(1)

            # Define list of output paths
            if "output_paths" in process:
                for key, value in process["output_paths"].items():
                    if key in self.outputs_by_process[name]:
                        if value in self.output_paths:
                            print()
                            print(colored(f'(X) {value} is defined twice in "output_paths".', "red"))
                            sys.exit(1)
                        else:
                            self.output_paths.append(value)
                    else:
                        print()
                        print(colored(f"(X) {key} is not an output path of {name}.", "red"))
                        sys.exit(1)

            # Define list of outputs for analysis
            if "overall_analysis" in process:
                for key, value in process["overall_analysis"].items():
                    if key in self.analysis_by_process[name]:
                        self.overall_analysis.append(value)
                    else:
                        print()
                        print(colored(f"(X) {key} is not an output analysis of {name}.", "red"))
                        sys.exit(1)

                    if value not in self.output_paths:
                        print()
                        print(colored(f'(X) {value} defined in {name} "overall_analysis" must be defined in previous process "output_paths".', "red"))
                        sys.exit(1)

        # Delete duplicates
        self.user_params = list(dict.fromkeys(self.user_params))
        self.user_paths = list(dict.fromkeys(self.user_paths))
        self.overall_analysis = list(dict.fromkeys(self.overall_analysis))

        # Define analysis settings
        for output in self.overall_analysis:
            self.analysis_settings[output] = {}

        for proc, settings in self.settings_by_process.items():
            if settings:
                for out, setting in settings.items():
                    output = self.analysis_plug[proc][out]
                    self.analysis_settings[output].update(setting)

    def print_processes(self):
        """Print processes"""

        for proc in self.list_workflow:

            name = proc["process"].__name__

            # Printing
            print()
            print(
                colored(f"| {name} |", "magenta"),
            )

            # ---------------- #
            # Input parameters #
            # ---------------- #
            print(
                colored(f"> Input Parameter(s) :", "blue"),
            )
            if len(self.params_by_process[name]) == 0:
                print(
                    colored("None.", "blue"),
                )
            else:
                lines_proc = []
                lines_user = []
                error = False
                for key, value in self.params_by_process[name].items():

                    # Process
                    text_type_proc = f"({value[1]})"
                    text_variable_proc = key
                    lines_proc.append((text_type_proc, text_variable_proc))

                    # User
                    if self.params_plug[name][key] is not None:
                        text_variable_user = str(self.params_plug[name][key][0])
                        text_definition_user = f"({self.params_plug[name][key][1]})"
                        lines_user.append((text_variable_user, text_definition_user))
                    else:
                        lines_user.append(("Not defined", "(X)"))
                        error = True

                type_proc_width = max(len(t) for t, _ in lines_proc)+1
                variable_proc_width = max(len(p) for _, p in lines_proc)+1
                variable_user_width = max(len(t) for t, _ in lines_user)+1
                definition_user_width = max(len(p) for _, p in lines_user)+1

                for (type_proc, var_proc), (user_var, user_def) in zip(lines_proc, lines_user):
                    proc_str = type_proc.ljust(type_proc_width)+var_proc.ljust(variable_proc_width)+"-----|"
                    user_str = "|----- "+user_var.ljust(variable_user_width)+user_def.ljust(definition_user_width)
                    if "(X)" in user_str: color = "red"
                    else: color = "green"
                    print(colored(proc_str, "blue")+colored(user_str, color))

                if error:
                    print()
                    print(colored('(X) Please define all input parameters either in "user_params" or "hard_params".', "red"))
                    sys.exit(1)

            # ----------- #
            # Input paths #
            # ----------- #
            print(
                colored(f"> Input Path(s) :", "blue"),
            )
            if len(self.paths_by_process[name]) == 0:
                print(
                    colored("None.", "blue"),
                )
            else:
                lines_proc = []
                lines_user = []
                error = False
                for path in self.paths_by_process[name]:

                    # Process
                    lines_proc.append(path)

                    # User
                    if self.paths_plug[name][path] is not None:
                        text_variable_user = self.paths_plug[name][path][0]
                        text_definition_user = f"({self.paths_plug[name][path][1]})"
                        lines_user.append((text_variable_user, text_definition_user))
                    else:
                        lines_user.append(("Not defined", "(X)"))
                        error = True

                proc_width = max(len(t) for t in lines_proc)+1
                variable_user_width = max(len(t) for t, _ in lines_user)+1
                definition_user_width = max(len(p) for _, p in lines_user)+1

                for (proc), (user_var, user_def) in zip(lines_proc, lines_user):
                    proc_str = proc.ljust(proc_width)+"-----|"
                    user_str = "|----- "+user_var.ljust(variable_user_width)+user_def.ljust(definition_user_width)
                    if "(X)" in user_str: color = "red"
                    else: color = "green"
                    print(colored(proc_str, "blue")+colored(user_str, color))

                if error:
                    print()
                    print(colored('(X) Please define all input paths either in "user_paths" or "required_paths".', "red"))
                    sys.exit(1)

            # ---------------- #
            # Input analysis #
            # ---------------- #
            print(
                colored(f"> Input Analysis :", "blue"),
            )
            if len(self.analysis_by_process[name]) == 0:
                print(
                    colored("None.", "blue"),
                )
            else:
                lines_proc = []
                lines_user = []
                error = False
                for out in self.analysis_by_process[name]:

                    # Process
                    lines_proc.append(out)

                    # User
                    if self.analysis_plug[name][out] is not None:
                        text_variable_user = self.analysis_plug[name][out]
                        text_definition_user = "(overall_analysis)"
                        lines_user.append((text_variable_user, text_definition_user))
                    else:
                        lines_user.append(("Not defined", "(X)"))
                        error = True

                proc_width = max(len(t) for t in lines_proc)+1
                variable_user_width = max(len(t) for t, _ in lines_user)+1
                definition_user_width = max(len(p) for _, p in lines_user)+1

                for (proc), (user_var, user_def) in zip(lines_proc, lines_user):
                    proc_str = proc.ljust(proc_width)+"-----|"
                    user_str = "|----- "+user_var.ljust(variable_user_width)+user_def.ljust(definition_user_width)
                    if "(X)" in user_str: color = "red"
                    else: color = "green"
                    print(colored(proc_str, "blue")+colored(user_str, color))

                if error:
                    print()
                    print(colored('(X) Please define all output analysis in "overall_analysis".', "red"))
                    sys.exit(1)

            # ------------ #
            # Output paths #
            # ------------ #
            print(
                colored(f"> Output Path(s) :", "blue"),
            )
            if len(self.outputs_by_process[name]) == 0:
                print(
                    colored("None.", "blue"),
                )
            else:
                lines_proc = []
                lines_user = []
                error = False
                for path in self.outputs_by_process[name]:

                    # Process
                    lines_proc.append(path)

                    # User
                    if self.outputs_plug[name][path] is not None:
                        text_variable_user = self.outputs_plug[name][path]
                        text_definition_user = "(output_paths)"
                        lines_user.append((text_variable_user, text_definition_user))
                    else:
                        lines_user.append(("Not defined", "(X)"))
                        error = True

                proc_width = max(len(t) for t in lines_proc)+1
                variable_user_width = max(len(t) for t, _ in lines_user)+1
                definition_user_width = max(len(p) for _, p in lines_user)+1

                for (proc), (user_var, user_def) in zip(lines_proc, lines_user):
                    proc_str = proc.ljust(proc_width)+"-----|"
                    user_str = "|----- "+user_var.ljust(variable_user_width)+user_def.ljust(definition_user_width)
                    if "(X)" in user_str: color = "red"
                    else: color = "green"
                    print(colored(proc_str, "blue")+colored(user_str, color))

                if error:
                    print()
                    print(colored('(X) Please define all output paths in "output_paths".', "red"))
                    sys.exit(1)

    def set_user_params_types(self):
        """Set types of user parameters"""

        # Gather all types of parameters
        for proc, params in self.params_by_process.items():
            for param, type in params.items():
                user_param = self.params_plug[proc][param][0]
                if user_param in self.user_params:
                    if (user_param in self.params_type) and (self.params_type[user_param][0] != type[0]):
                        print()
                        print(colored(f"(X) {user_param} is defined both as ({self.params_type[user_param][1]}) and ({type[1]}) :", "red"))
                        print(colored(f'> Please consider defining a new user parameter in "user_params".', "red"))
                        sys.exit(1)
                    self.params_type[user_param] = type

    def print_io(self):
        """Print inputs / outputs"""

        # Printing
        print()
        print(
            colored("> INPUTS <", "blue", attrs=["reverse"]),
        )

        # Print input parameters
        print()
        print(
            colored(f"| User Parameters |", "magenta"),
        )
        for param, type in self.params_type.items():
            print(
                colored(f"> {param} ({type[1]})", "blue"),
            )
        if len(list(self.params_type.items())) == 0:
            print(
                colored("None.", "blue"),
            )

        # Print input paths
        print()
        print(
            colored(f"| User Paths |", "magenta"),
        )
        for path in self.user_paths:
            print(
                colored(f"> {path}", "blue"),
            )
        if len(self.user_paths) == 0:
            print(
                colored("None.", "blue"),
            )

        # Printing
        print()
        print(
            colored("> OUTPUTS <", "blue", attrs=["reverse"]),
        )
        print()
        for path in self.output_paths:
            print(
                colored(f"> {path}", "blue"),
            )
        if len(self.output_paths) == 0:
            print(
                colored("None.", "blue"),
            )

    def define_studies(self):
        """Define studies"""

        # ---------------------------- #
        # Initialize studies json file #
        # ---------------------------- #
        self.studies_file = self.working_dir / "studies.json"
        if self.studies_file.exists():
            with open(self.studies_file) as f:
                self.dict_studies = json.load(f)
        else:
            self.dict_studies["studies"] = []
            self.dict_studies["config"] = {}
            with open(self.studies_file, "w") as f:
                json.dump(self.dict_studies, f, indent=4)

        print()
        print(
            colored("> STUDIES <", "blue", attrs=["reverse"]),
        )

        if len(self.dict_studies["studies"]) == 0:
            print()
            print(colored(f"(X) Please declare at least one study in file :", "red"))
            print(colored(f"> {str(self.studies_file)}", "red"))
            sys.exit(1)
        else:
            self.studies = self.dict_studies["studies"]

    def init_studies(self):
        """Initialize studies"""

        # Clean studies
        for study in list(self.dict_studies["config"].keys()):
            if study not in self.studies:
                del self.dict_studies["config"][study]

        # Clean input parameters
        for study in list(self.dict_studies["config"].keys()):
            for param in list(self.dict_studies["config"][study]["user_params"]):
                if param not in self.user_params:
                    del self.dict_studies["config"][study]["user_params"][param]

        # Clean input paths
        for study in list(self.dict_studies["config"].keys()):
            for path in list(self.dict_studies["config"][study]["user_paths"]):
                if path not in self.user_paths:
                    del self.dict_studies["config"][study]["user_paths"][path]

        # Clean output paths
        for study in list(self.dict_studies["config"].keys()):
            for path in list(self.dict_studies["config"][study]["clean_outputs"]):
                if path not in self.output_paths:
                    del self.dict_studies["config"][study]["clean_outputs"][path]

        # Initialize input parameters/paths
        for study in self.studies:

            if study not in self.dict_studies["config"]:
                self.dict_studies["config"][study] = {
                    "execute": True,
                    "user_params": {},
                    "user_paths": {},
                    "clean_outputs": {},
                }

            for param in self.user_params:
                if param not in self.dict_studies["config"][study]["user_params"]:
                    if study == "Default":
                        self.dict_studies["config"][study]["user_params"][param] = False
                    else:
                        self.dict_studies["config"][study]["user_params"][param] = None

            for file in self.user_paths:
                if file not in self.dict_studies["config"][study]["user_paths"]:
                    if study == "Default":
                        self.dict_studies["config"][study]["user_paths"][file] = False
                    else:
                        self.dict_studies["config"][study]["user_paths"][file] = None

            for path in self.output_paths:
                if path not in self.dict_studies["config"][study]["clean_outputs"]:
                    self.dict_studies["config"][study]["clean_outputs"][path] = False

            # Reordering
            self.dict_studies["config"][study]["user_params"] = {k: self.dict_studies["config"][study]["user_params"][k] for k in self.user_params}
            self.dict_studies["config"][study]["user_paths"] = {k: self.dict_studies["config"][study]["user_paths"][k] for k in self.user_paths}

        # Write studies json file
        with open(self.studies_file, "w") as f:
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
                if (self.dict_studies["config"][study]["user_params"] != dict_study["user_params"]) or \
                   (self.dict_studies["config"][study]["user_paths"] != dict_study["user_paths"]):
                    self.studies_modif[study] = True

    def test_studies_settings(self):
        """Check if studies has been properly configured"""

        # Loop over studies
        for study in self.studies:

            self.studies_messages[study] = []
            self.studies_config[study] = True

            for param in self.user_params:
                if self.dict_studies["config"][study]["user_params"][param] is None:
                    self.studies_messages[study].append(f"(X) {param} not configured.")
                    self.studies_config[study] = False
                else:
                    if self.dict_studies["config"][study]["user_params"][param]: text = "variable"
                    else: text = "fixed"
                    self.studies_messages[study].append(f"(V) {param} is {text}.")

            for file in self.user_paths:
                if self.dict_studies["config"][study]["user_paths"][file] is None:
                    self.studies_messages[study].append(f"(X) {file} not configured.")
                    self.studies_config[study] = False
                else:
                    if self.dict_studies["config"][study]["user_paths"][file]: text = "variable"
                    else: text = "fixed"
                    self.studies_messages[study].append(f"(V) {file} is {text}.")

    def print_studies(self):
        """Print studies"""

        for study in self.studies:

            # Printing
            print()
            print(
                colored(f"| {study} |", "magenta"),
            )
            if self.studies_modif[study]:
                print(
                    colored(f"(!) Configuration has been modified.", "yellow"),
                )
                self.clean_output_tree(study)

                # Delete analysis file
                path = Path(study) / "analysis.json"
                if path.exists(): path.unlink()

            for message in self.studies_messages[study]:
                if "(V)" in message: print(colored(message, "green"))
                elif "(X)" in message: print(colored(message, "red"))

            if not self.studies_config[study]:
                print()
                print(colored(f"(X) Please configure file :", "red"))
                print(colored(f"> {str(Path.cwd() / 'studies.json')}", "red"))
                sys.exit(1)

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
                        "silent": self.silent,
                    }

            # Reordering
            self.dict_process[study] = {k: self.dict_process[study][k] for k in self.list_processes}

            # Write studies json file
            with open(process_file, "w") as f:
                json.dump(self.dict_process[study], f, indent=4)

    def configure_inputs(self):
       """Configure inputs with lists of fixed/variable parameters/paths"""

       for study in self.studies:

            # Define list of fixed/variable parameters
            fixed_params = []
            variable_params = []
            for key, value in self.dict_studies["config"][study]["user_params"].items():
                if value is True: variable_params.append(key)
                else: fixed_params.append(key)

            # Define list of fixed/variable paths
            fixed_paths = []
            variable_paths = []
            for key, value in self.dict_studies["config"][study]["user_paths"].items():
                if value is True: variable_paths.append(key)
                else: fixed_paths.append(key)

            self.fixed_params[study] = fixed_params
            self.variable_params[study] = variable_params
            self.fixed_paths[study] = fixed_paths
            self.variable_paths[study] = variable_paths

    def init_data_tree(self):
        """Initialize data tree"""

        # Loop over studies
        for study in self.studies:

            # Initialize study directory
            study_dir:Path = self.working_dir / study
            study_dir.mkdir(
                exist_ok=True,
                parents=True,
            )

            # Write study json file
            with open(study_dir / ".study.json", "w") as f:
                json.dump(self.dict_studies["config"][study], f, indent=4)

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

                    # Set default execution
                    df_inputs["EXECUTE"] = df_inputs["EXECUTE"].fillna(1).astype(int)

                    # Write input dataframe
                    df_inputs.to_csv(
                        path_or_buf=inputs_file,
                    )

                # Define list of datasets
                self.dict_datasets[study] = df_inputs.index.tolist()

            else:
                # Delete file
                if inputs_file.exists(): inputs_file.unlink()

            # Initialize inputs json file
            inputs_file:Path = study_dir / "inputs.json"
            if (len(self.fixed_params[study]) > 0) or \
               (len(self.fixed_paths[study]) > 0) or \
               (len(self.variable_paths[study]) > 0) :

                # Create file
                if not inputs_file.exists():

                    # Initialize dictionary
                    dict_inputs = {}
                    if len(self.fixed_params[study]) > 0:
                        for param in self.fixed_params[study]:
                            dict_inputs[param] = None
                    if len(self.fixed_paths[study]) > 0:
                        for path in self.fixed_paths[study]:
                            dict_inputs[path] = None
                    if len(self.variable_paths[study]) > 0:
                        for path in self.variable_paths[study]:
                            dict_inputs[path] = {}
                            for index in df_inputs.index:
                                dict_inputs[path][index] = None

                    # Write json
                    with open(inputs_file, "w") as f:
                        json.dump(dict_inputs, f, indent=4)

                # Update file
                else:

                    # Read inputs json
                    with open(inputs_file) as f:
                        dict_inputs = json.load(f)

                    # Update fixed parameters
                    dict_fixed_params = {k: dict_inputs.get(k, None) for k in self.fixed_params[study]}

                    # Update fixed paths
                    dict_fixed_paths = {}
                    for path in self.fixed_paths[study]:
                        value = dict_inputs.get(path, None)
                        if isinstance(value, dict):
                            dict_fixed_paths[path] = None
                        else:
                            dict_fixed_paths[path] = value

                    # Update variable paths
                    dict_variable_paths = {}
                    for path in self.variable_paths[study]:
                        existing_values = dict_inputs.get(path, {})
                        if not isinstance(existing_values, dict):
                            existing_values = {}
                        dict_variable_paths[path] = {
                            idx: existing_values.get(idx, None)
                            for idx in df_inputs.index
                        }

                    # Update inputs dictionnary
                    dict_inputs = {**dict_fixed_params, **dict_fixed_paths, **dict_variable_paths}

                    # Write inputs json
                    with open(inputs_file, "w") as f:
                        json.dump(dict_inputs, f, indent=4)

                self.dict_inputs[study] = dict_inputs

            else:

                # Delete file
                if inputs_file.exists(): inputs_file.unlink()

                self.dict_inputs[study] = {}

            # Initialize inputs directory
            inputs_dir:Path = study_dir / "0_inputs"
            if len(self.user_paths) > 0:

                # Create inputs directory (if necessary)
                inputs_dir.mkdir(
                    exist_ok=True,
                    parents=True,
                )

                # Delete fixed paths (if necessary)
                input_paths = [f for f in inputs_dir.iterdir()]
                for path in input_paths:
                    resolved_path = path.resolve().name
                    if (resolved_path not in self.fixed_paths[study]) and (resolved_path != "0_datasets"):
                        if Path(path).is_file(): path.unlink()
                        else: shutil.rmtree(path)

                # Update inputs subfolders for variable paths
                datasets_dir:Path = inputs_dir / "0_datasets"
                if len(self.variable_paths[study]) > 0:

                    # Create datasets directory (if necessary)
                    datasets_dir.mkdir(
                        exist_ok=True,
                        parents=True,
                    )

                    # Create subfolders (if necessary)
                    for index in df_inputs.index:

                        inputs_subfolder:Path = datasets_dir / index
                        inputs_subfolder.mkdir(
                            exist_ok=True,
                            parents=True,
                        )

                        # Delete variable paths (if necessary)
                        input_paths = [f for f in inputs_subfolder.iterdir()]
                        for path in input_paths:
                            resolved_path = path.resolve().name
                            if resolved_path not in self.variable_paths[study]:
                                if Path(path).is_file(): path.unlink()
                                else: shutil.rmtree(path)

                    # Delete subfolders (if necessary)
                    inputs_subfolders = [f for f in datasets_dir.iterdir() if f.is_dir()]
                    for folder in inputs_subfolders:
                        id = os.path.split(folder)[-1]
                        if id not in self.dict_datasets[study]:
                            shutil.rmtree(folder)

                else:

                    # Delete datasets folder (if necessary)
                    if datasets_dir.exists(): shutil.rmtree(datasets_dir)

            else:
                # Delete inputs directory (if necessary)
                if inputs_dir.exists(): shutil.rmtree(inputs_dir)

    def clean_output_tree(self,
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
            self.dict_user_paths[study] = {}

            # Fixed parameters
            if len(self.fixed_params[study]) > 0:
                data = self.dict_inputs[study]
                self.dict_fixed_params[study] = {k: data[k] for k in self.fixed_params[study] if k in data}
            else:
                self.dict_fixed_params[study] = {}

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

            # Fixed paths
            dict_input_paths = {}
            for file in self.fixed_paths[study]:
                if self.dict_inputs[study][file] is not None:
                    dict_input_paths[file] = self.dict_inputs[study][file]
                else:
                    dict_input_paths[file] = str(Path(os.getcwd()) / "0_inputs" / file)

            self.dict_user_paths[study] = {**self.dict_user_paths[study], **dict_input_paths}

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
                        if self.dict_inputs[study][file][idx] is not None:
                            dict_input_paths[file][idx] = self.dict_inputs[study][file][idx]
                        else:
                            dict_input_paths[file][idx] = str(Path(os.getcwd()) / "0_inputs" / "0_datasets" / idx / file)

                self.dict_user_paths[study] = {**self.dict_user_paths[study], **dict_input_paths}

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
                    if not isinstance(value, self.params_type[param][0]):
                        self.fixed_params_messages[study].append(f"(!) {param} ({self.params_type[param][1]} expected)")
                    else:
                        self.fixed_params_messages[study].append(f"(V) {param}")

            # Fixed paths
            for file in self.fixed_paths[study]:
                file_path:Path = Path(self.dict_user_paths[study][file])
                if not file_path.exists():
                    self.fixed_paths_messages[study].append(f"(X) {file}")
                    self.fixed_paths_config[study] = False
                else:
                    self.fixed_paths_messages[study].append(f"(V) {file}")

            # Variable inputs
            if (len(self.variable_params[study]) > 0) or \
               (len(self.variable_paths[study]) > 0):

                for index in self.dict_variable_params[study].index:

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
                            if isinstance(value, (np.integer, np.floating, np.bool_)):
                                value = value.item()
                            if not isinstance(value, self.params_type[param][0]):
                                self.variable_params_messages[study][index].append(f"(!) {param} ({self.params_type[param][1]} expected)")
                            else:
                                self.variable_params_messages[study][index].append(f"(V) {param}")

                    # Variable paths
                    for file in self.variable_paths[study]:
                        file_path:Path = Path(self.dict_user_paths[study][file][index])
                        if not file_path.exists():
                            self.variable_paths_messages[study][index].append(f"(X) {file}")
                            self.variable_paths_config[study][index] = False
                        else:
                            self.variable_paths_messages[study][index].append(f"(V) {file}")

            # Go back to working directory
            os.chdir(self.working_dir)

    def print_inputs_settings(self):
        """Print inputs settings"""

        print()
        print(
            colored("> SETTINGS <", "blue", attrs=["reverse"]),
        )
        for study in self.studies:

            # Define study directory
            study_dir:Path = self.working_dir / study

            # Go to study directory
            os.chdir(study_dir)

            # Printing
            print()
            print(colored(f"| {study} |", "magenta"))

            # ------------ #
            # Fixed inputs #
            # ------------ #
            list_text = [colored(f"> Common :", "blue")]
            list_errors = []
            config = True
            type_error = False

            # Fixed parameters
            for message in self.fixed_params_messages[study]:
                if "(V)" in message:
                    list_text.append(colored(message, "green"))
                elif "(X)" in message:
                    list_text.append(colored(message, "red"))
                    if config:
                        list_errors.append(colored(f"> {str(Path.cwd() / 'inputs.json')}", "red"))
                    config = False
                elif "(!)" in message:
                    list_text.append(colored(message, "yellow"))
                    type_error = True

            # Fixed paths
            for i, message in enumerate(self.fixed_paths_messages[study]):
                if "(V)" in message:
                    list_text.append(colored(message, "green"))
                elif "(X)" in message:
                    file = self.fixed_paths[study][i]
                    path = self.dict_user_paths[study][file]
                    list_text.append(colored(message, "red"))
                    list_errors.append(colored(f"> {path}", "red"))

            # Printing
            if len(list_text) == 1:
                print(colored(f"None.", "blue"))
            else:
                print(*list_text)

            if not self.fixed_params_config[study] or not self.fixed_paths_config[study]:
                print()
                print(colored(f"(X) Please set inputs :", "red"))
                for error in list_errors:
                    print(error)
                sys.exit(1)

            if type_error:
                print()
                print(colored(f"(X) Please set parameter(s) with expected type(s) in file :", "red"))
                print(colored(f"> {str(Path.cwd() / 'inputs.json')}", "red"))
                sys.exit(1)

            # --------------- #
            # Variable inputs #
            # --------------- #
            list_errors = []
            config = True
            type_error = False

            if (len(self.variable_params[study]) > 0) or \
               (len(self.variable_paths[study]) > 0):

                # Check if datasets have been defined
                if len(self.dict_variable_params[study].index) == 0:
                    print()
                    print(colored(f"(X) Please declare at least one experiment in file :", "red"))
                    print(colored(f"> {str(Path.cwd() / 'inputs.csv')}", "red"))
                    sys.exit(1)

                for index in self.dict_variable_params[study].index:

                    list_text = [colored(f"> {index} :", "blue")]

                    # Variable parameters
                    for message in self.variable_params_messages[study][index]:
                        if "(V)" in message:
                            list_text.append(colored(message, "green"))
                        elif "(X)" in message:
                            list_text.append(colored(message, "red"))
                            if config:
                                list_errors.append(colored(f"> {str(Path.cwd() / 'inputs.csv')}", "red"))
                            config = False
                        elif "(!)" in message:
                            list_text.append(colored(message, "yellow"))
                            type_error = True

                    # Variable paths
                    for i, message in enumerate(self.variable_paths_messages[study][index]):
                        if "(V)" in message:
                            list_text.append(colored(message, "green"))
                        elif "(X)" in message:
                            file = self.variable_paths[study][i]
                            path = self.dict_user_paths[study][file][index]
                            list_text.append(colored(message, "red"))
                            list_errors.append(colored(f"> {path}", "red"))

                    # Printing
                    print(*list_text)

                list_errors.sort(key=lambda x: 0 if "inputs.csv" in x else 1)
                if len(list_errors) > 0:
                    print()
                    print(colored(f"(X) Please set inputs :", "red"))
                    for error in list_errors:
                        print(error)
                    sys.exit(1)

                if type_error:
                    print()
                    print(colored(f"(X) Please set parameter(s) with expected type(s) in file :", "red"))
                    print(colored(f"> {str(Path.cwd() / 'inputs.csv')}", "red"))
                    sys.exit(1)

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
                for path in self.output_paths:
                    dict_paths[path] = None

            # Purge old datasets
            for key, value in dict_paths.items():
                if isinstance(value, dict):
                    # List of datasets to delete
                    to_delete = [dataset for dataset in value if dataset not in self.dict_datasets[study]]
                    for dataset in to_delete:
                        del dict_paths[key][dataset]

            self.dict_paths[study] = dict_paths

    def update_analysis(self):

        # Loop over studies
        for study in self.studies:

            # Define study directory
            study_dir:Path = self.working_dir / study

            # Define analysis file
            analysis_file = study_dir / "analysis.json"

            # Initialize analysis file
            if os.path.exists(analysis_file):
                with open(analysis_file) as f:
                    self.dict_analysis[study] = json.load(f)
            else:
                self.dict_analysis[study] = {}

            # Browse all outputs
            for out, value in self.dict_paths[study].items():

                if out in self.analysis_settings:
                    dict_out = self.analysis_settings[out]
                else:
                    dict_out = {}

                if out not in self.dict_analysis[study]:
                    self.dict_analysis[study][out] = {}
                    if isinstance(value, dict):
                        for case in value:
                            self.dict_analysis[study][out][case] = dict_out

                else:
                    if isinstance(value, dict):
                        for case in value:
                            if case not in self.dict_analysis[study][out]:
                                self.dict_analysis[study][out][case] = dict_out

                        cases_to_delete = []
                        for case in self.dict_analysis[study][out]:
                            if case not in value:
                                cases_to_delete.append(case)

                        for case in cases_to_delete:
                            if case in self.dict_analysis[study][out]:
                                del self.dict_analysis[study][out][case]

            with open(analysis_file, "w") as f:
                json.dump(self.dict_analysis[study], f, indent=4)

    def clean_outputs(self):
        """Clean outputs."""

        # Function to remove output path, either file or directory
        def _remove_output(output: str):
            output_path = Path(output)
            if output_path.exists():
                if output_path.is_dir():
                    shutil.rmtree(output)
                else:
                    output_path.unlink()

        # Loop over studies
        for study, study_dict in self.dict_studies["config"].items():

            # Delete specified outputs
            for key, value in study_dict["clean_outputs"].items():
                if value:
                    if isinstance(self.dict_paths[study][key], str):
                        _remove_output(self.dict_paths[study][key])
                    if isinstance(self.dict_paths[study][key], dict):
                        for _, value in self.dict_paths[study][key].items():
                            _remove_output(value)

    def purge_output_datasets(self,
        study: str,
    ):
        """Purge output datasets for a specific study"""

        datasets_paths = [f for f in Path.cwd().iterdir()]
        for path in datasets_paths:
            resolved_path = path.resolve().name
            if resolved_path not in self.dict_datasets[study]:
                shutil.rmtree(path)

    def update_workflow_diagram(self,
        process: Process,
    ):
        """Update workflow diagram for specific process"""

        self.diagram[process.name] = {
            "params": list(process.params.values()),
            "allparams": process.allparams,
            "paths": list(process.paths.values()),
            "allpaths": process.allpaths,
            "required_paths": list(process.required_paths.values()),
            "output_paths": list(process.output_paths.values()),
        }

    def __call__(self):
        """Launch workflow of processes."""

        # --------------- #
        # Launch workflow #
        # --------------- #
        print()
        print(
            colored("> RUNNING <", "blue", attrs=["reverse"]),
        )

        for study, dict_study in self.dict_studies["config"].items():

            # Check if study must be executed
            if not dict_study["execute"]:

                # Printing
                print()
                print(
                    colored(f"| {study} |", "magenta"),
                )
                print()
                print(colored("(!) Study is skipped.", "yellow"))

                continue

            study_dir:Path = self.working_dir / study
            os.chdir(study_dir)

            for step, proc in enumerate(self.list_workflow):

                # Update analysis
                self.update_analysis()

                if "hard_params" in proc: dict_hard_params = proc["hard_params"]
                else: dict_hard_params = {}
                if "user_params" in proc: user_params = proc["user_params"]
                else: user_params = {}
                if "user_paths" in proc: user_paths = proc["user_paths"]
                else: user_paths = {}
                if "required_paths" in proc: required_paths = proc["required_paths"]
                else: required_paths = {}
                if "output_paths" in proc: output_paths = proc["output_paths"]
                else: output_paths = {}
                if "overall_analysis" in proc: overall_analysis = proc["overall_analysis"]
                else: overall_analysis = {}

                # Define class object for the current process
                process = proc["process"]
                this_process:Process = process(
                    study=study,
                    df_user_params=self.dict_variable_params[study],
                    dict_user_params=self.dict_fixed_params[study],
                    dict_user_paths=self.dict_user_paths[study],
                    dict_paths=self.dict_paths[study],
                    params=user_params,
                    paths=user_paths,
                    dict_hard_params=dict_hard_params,
                    fixed_params=self.fixed_params[study],
                    variable_params=self.variable_params[study],
                    fixed_paths=self.fixed_paths[study],
                    variable_paths=self.variable_paths[study],
                    required_paths=required_paths,
                    output_paths=output_paths,
                    overall_analysis=overall_analysis,
                    dict_analysis=self.dict_analysis[study],
                    silent=self.dict_process[study][self.list_processes[step]]["silent"],
                    diagram=self.diagram,
                )

                # Define process name
                this_process.name = this_process.__class__.__name__

                # Define working folder associated to the current process
                folder_name = f"{step+1}_{this_process.name}"
                folder_path:Path = study_dir / folder_name
                folder_path.mkdir(exist_ok=True, parents=True)
                os.chdir(folder_path)

                # Initialize process
                this_process.initialize()

                # Check if process must be executed
                if not self.dict_process[study][self.list_processes[step]]["execute"]:

                    # Printing
                    print()
                    print(
                        colored(f"| {study} | {this_process.name} |", "magenta"),
                    )
                    print()
                    print(colored("(!) Process is skipped.", "yellow"))

                    # Update workflow diagram
                    self.update_workflow_diagram(this_process)

                    continue

                if this_process.is_case:

                    # Define sub-folders associated to each ID of the inputs dataframe
                    for idx in this_process.df_params.index:

                        # Printing
                        print()
                        print(
                            colored(f"| {study} | {this_process.name} | {idx} |", "magenta"),
                        )

                        # Check if dataset must be executed
                        if self.dict_variable_params[study].loc[idx, "EXECUTE"] == 0:

                            # Printing
                            print()
                            print(colored("(!) Experiment is skipped.", "yellow"))

                            # Go back to working folder
                            os.chdir(folder_path)

                            # Purge old output datasets
                            self.purge_output_datasets(study)

                            # Update workflow diagram
                            self.update_workflow_diagram(this_process)

                            continue

                        # Update process index
                        this_process.index = idx

                        subfolder_path = study_dir / folder_name / str(idx)
                        subfolder_path.mkdir(exist_ok=True, parents=True)
                        os.chdir(subfolder_path)

                        # Launch process
                        this_process()
                        this_process.finalize()

                        # Go back to working folder
                        os.chdir(folder_path)

                        # Purge old output datasets
                        self.purge_output_datasets(study)

                else:

                    # Printing
                    print()
                    print(
                        colored(f"| {study} | {this_process.name} |", "magenta"),
                    )

                    # Launch process
                    this_process()
                    this_process.finalize()

                # Update workflow diagram
                self.update_workflow_diagram(this_process)

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

        # Go back to working directory
        os.chdir(self.working_dir)

        # Delete unecessary outputs
        self.clean_outputs()