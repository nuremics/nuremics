from __future__ import annotations

from pathlib import Path

import yaml
from platformdirs import user_config_path

from .workflow import WorkFlow
from .utils import resolve_process

CONFIG_PATH = user_config_path(
    appname="nuRemics",
    appauthor=False,
)


class Application:

    def __init__(
        self,
        app_id: list,
        apps_dir: Path,
        stage: str = "run",
        config_path: Path = CONFIG_PATH,
        silent: bool = False,
    ) -> None:

        apps_factory = {}
        for f in apps_dir.glob("apps/**/*.yaml"):
            category = f.parent.parent.name
            app_name = f.parent.name

            if category not in apps_factory:
                apps_factory[category] = {}

            apps_factory[category][app_name] = f

        app_file = apps_factory[app_id[0]][app_id[1]]
        with open(app_file) as f:
            dict_app = yaml.safe_load(f)

        self.stage = stage
        self.list_workflow = dict_app["workflow"]
        self.default_params = dict_app["default_params"]

        for step in self.list_workflow:
            step["process"] = resolve_process(step["process"])
        
        self.workflow = WorkFlow(
            app_name=app_file.parent.name,
            config_path=config_path,
            workflow=self.list_workflow,
            silent=silent,
        )

        self.workflow.print_logo()
        self.workflow.print_application()

        self.workflow.get_inputs()
        self.workflow.get_outputs()

        self.workflow.init_config()

        self.workflow.print_processes()

        self.workflow.set_user_params_types()

        self.workflow.print_io()

    def configure(self) -> None:

        self.workflow.set_working_directory()

        self.workflow.define_studies()
        self.workflow.init_studies()
        self.workflow.test_studies_modification()
        self.workflow.test_studies_settings()
        self.workflow.print_studies()

        self.workflow.configure_inputs()
        self.workflow.init_data_tree()

        self.workflow.init_process_settings()

    def settings(self) -> None:

        self.workflow.set_inputs()
        self.workflow.test_inputs_settings()
        self.workflow.print_inputs_settings()

        self.workflow.init_paths()

    def __call__(self) -> None:

        if self.stage == "config":
            self.configure()
        elif self.stage == "settings":
            self.configure()
            self.settings()
        elif self.stage == "run":
            self.configure()
            self.settings()
            self.workflow()