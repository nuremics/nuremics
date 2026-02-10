from __future__ import annotations

from pathlib import Path

from platformdirs import user_config_path

from .workflow import WorkFlow

CONFIG_PATH = user_config_path(
    appname="nuRemics",
    appauthor=False,
)


class Application:
    """Create application."""

    def __init__(
        self,
        app_name: str,
        config_path: Path = CONFIG_PATH,
        workflow: list = [],
        silent: bool = False,
    ):
        # ---------------------- #
        # Define workflow object #
        # ---------------------- #
        self.workflow = WorkFlow(
            app_name=app_name,
            config_path=config_path,
            workflow=workflow,
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

    def configure(self):

        self.workflow.set_working_directory()

        self.workflow.define_studies()
        self.workflow.init_studies()
        self.workflow.test_studies_modification()
        self.workflow.test_studies_settings()
        self.workflow.print_studies()

        self.workflow.configure_inputs()
        self.workflow.init_data_tree()

        self.workflow.init_process_settings()

    def settings(self):

        self.workflow.set_inputs()
        self.workflow.test_inputs_settings()
        self.workflow.print_inputs_settings()

        self.workflow.init_paths()

    def __call__(self):

        # --------------- #
        # Launch workflow #
        # --------------- #
        self.workflow()
