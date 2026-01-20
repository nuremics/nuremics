from __future__ import annotations

from platformdirs import user_config_path
from .workflow import WorkFlow

class Application:
    """Create application."""
    
    def __init__(
        self,
        app_name: str,
        # nuremics_dir: str,
        workflow: list = [],
        silent: bool = False,
    ):
        # ------------------------------ #
        # Define configuration directory #
        # ------------------------------ #
        config_path = user_config_path(
            appname="nuRemics",
            appauthor=False,
        )

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

        self.workflow.set_working_directory()

        self.workflow.define_studies()
        self.workflow.init_studies()
        self.workflow.test_studies_modification()
        self.workflow.test_studies_settings()
        self.workflow.print_studies()

        self.workflow.configure_inputs()
        self.workflow.init_data_tree()

        self.workflow.init_process_settings()

        self.workflow.set_inputs()
        self.workflow.test_inputs_settings()
        self.workflow.print_inputs_settings()

        self.workflow.init_paths()

    def __call__(self):
        
        # --------------- #
        # Launch workflow #
        # --------------- #
        self.workflow()