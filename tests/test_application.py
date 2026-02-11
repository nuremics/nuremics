import json
from pathlib import Path
from typing import Any

import pandas as pd
import pandas.testing as pdt
import pytest

from nuremics import Application

APP_NAME = "TEST_APP"


def test_state_settings(
    shared_tmp_path: Path,
    test_config: list[dict[str, Any]],
) -> None:

    workflow = test_config

    Application(
        app_name=APP_NAME,
        config_path=shared_tmp_path,
        workflow=workflow,
    )

    settings_file = shared_tmp_path / "settings.json"
    assert settings_file.is_file()

    with open(settings_file) as f:
        dict_settings = json.load(f)

    dict_settings_ref = {
        "default_working_dir": None,
        "apps":
        {
            "TEST_APP": {
                "working_dir": None,
            }
        }
    }
    assert dict_settings == dict_settings_ref

    dict_settings["apps"]["TEST_APP"]["working_dir"] = str(shared_tmp_path)
    with open(settings_file, "w") as f:
        json.dump(dict_settings, f, indent=4)

    with pytest.raises(SystemExit) as exc_info:
        app = Application(
            app_name=APP_NAME,
            config_path=shared_tmp_path,
            workflow=workflow,
        )
        app.configure()
        assert exc_info.value.code == 1
    
    with open(settings_file) as f:
        dict_settings = json.load(f)

    assert dict_settings["default_working_dir"] == str(shared_tmp_path)


def test_state_studies_config(
    shared_tmp_path: Path,
    test_config: list[dict[str, Any]],
) -> None:

    workflow = test_config

    with pytest.raises(SystemExit) as exc_info:
        app = Application(
            app_name=APP_NAME,
            config_path=shared_tmp_path,
            workflow=workflow,
        )
        app.configure()
        assert exc_info.value.code == 1

    app_dir: Path = shared_tmp_path / APP_NAME
    assert app_dir.is_dir()

    studies_file: Path = app_dir / "studies.json"
    assert studies_file.is_file()

    with open(studies_file) as f:
        dict_studies: dict = json.load(f)

    dict_studies_ref = {
        "studies": [],
        "config": {},
    }
    assert dict_studies == dict_studies_ref

    dict_studies["studies"] = [
        "Study1",
        "Study2",
    ]
    with open(studies_file, "w") as f:
        json.dump(dict_studies, f, indent=4)

    with pytest.raises(SystemExit) as exc_info:
        app = Application(
            app_name=APP_NAME,
            config_path=shared_tmp_path,
            workflow=workflow,
        )
        app.configure()
        assert exc_info.value.code == 1

    with open(studies_file) as f:
        dict_studies: dict = json.load(f)

    dict_studies_ref = {
        "studies": [
            "Study1",
            "Study2",
        ],
        "config": {
            "Study1": {
                "execute": True,
                "user_params": {
                    "parameter1": None,
                    "parameter2": None,
                    "parameter3": None,
                    "parameter4": None,
                    "parameter5": None,
                    "parameter6": None,
                },
                "user_paths": {
                    "input1.txt": None,
                    "input2": None,
                    "input3.txt": None,
                },
                "clean_outputs": {
                    "output1.txt": False,
                    "output2.txt": False,
                    "output3.txt": False,
                    "output4.txt": False,
                    "output5": False,
                    "output6.txt": False,
                }
            },
            "Study2": {
                "execute": True,
                "user_params": {
                    "parameter1": None,
                    "parameter2": None,
                    "parameter3": None,
                    "parameter4": None,
                    "parameter5": None,
                    "parameter6": None,
                },
                "user_paths": {
                    "input1.txt": None,
                    "input2": None,
                    "input3.txt": None,
                },
                "clean_outputs": {
                    "output1.txt": False,
                    "output2.txt": False,
                    "output3.txt": False,
                    "output4.txt": False,
                    "output5": False,
                    "output6.txt": False,
                }
            }
        }
    }
    assert dict_studies == dict_studies_ref
    
    dict_studies["config"]["Study1"]["user_params"]["parameter1"] = False
    dict_studies["config"]["Study1"]["user_params"]["parameter2"] = False
    dict_studies["config"]["Study1"]["user_params"]["parameter3"] = False
    dict_studies["config"]["Study1"]["user_params"]["parameter4"] = False
    dict_studies["config"]["Study1"]["user_params"]["parameter5"] = False
    dict_studies["config"]["Study1"]["user_params"]["parameter6"] = True
    dict_studies["config"]["Study1"]["user_paths"]["input1.txt"] = True
    dict_studies["config"]["Study1"]["user_paths"]["input2"] = False
    dict_studies["config"]["Study1"]["user_paths"]["input3.txt"] = False

    dict_studies["config"]["Study2"]["user_params"]["parameter1"] = False
    dict_studies["config"]["Study2"]["user_params"]["parameter2"] = False
    dict_studies["config"]["Study2"]["user_params"]["parameter3"] = False
    dict_studies["config"]["Study2"]["user_params"]["parameter4"] = True
    dict_studies["config"]["Study2"]["user_params"]["parameter5"] = True
    dict_studies["config"]["Study2"]["user_params"]["parameter6"] = False
    dict_studies["config"]["Study2"]["user_paths"]["input1.txt"] = False
    dict_studies["config"]["Study2"]["user_paths"]["input2"] = True
    dict_studies["config"]["Study2"]["user_paths"]["input3.txt"] = True

    with open(studies_file, "w") as f:
        json.dump(dict_studies, f, indent=4)


def test_state_set_inputs(
    shared_tmp_path: Path,
    test_config: list[dict[str, Any]],
) -> None:

    workflow = test_config
    
    with pytest.raises(SystemExit) as exc_info:
        app = Application(
            app_name=APP_NAME,
            config_path=shared_tmp_path,
            workflow=workflow,
        )
        app.configure()
        app.settings()
        assert exc_info.value.code == 1

    studies_file: Path = shared_tmp_path / APP_NAME / "studies.json"
    with open(studies_file) as f:
        dict_studies: dict = json.load(f)

    for study in ["Study1", "Study2"]:

        study_dir: Path = shared_tmp_path / APP_NAME / study
        assert study_dir.is_dir()

        inputs_dir: Path = study_dir / "0_inputs"
        assert inputs_dir.is_dir()

        datasets_dir: Path = inputs_dir / "0_datasets"
        assert datasets_dir.is_dir()

        inputs_csv: Path = study_dir / "inputs.csv"
        assert inputs_csv.is_file()

        inputs_json: Path = study_dir / "inputs.json"
        assert inputs_json.is_file()

        process_json: Path = study_dir / "process.json"
        assert process_json.is_file()

        study_json: Path = study_dir / ".study.json"
        assert study_json.is_file()

        df_inputs = pd.read_csv(inputs_csv)
        with open(inputs_json) as f:
            dict_inputs: dict = json.load(f)
        with open(process_json) as f:
            dict_process: dict = json.load(f)
        with open(study_json) as f:
            dict_study: dict = json.load(f)
        
        assert dict_study == dict_studies["config"][study]

        dict_process_ref = {
            "Process1": {
                "execute": True,
                "silent": False
            },
            "Process2": {
                "execute": True,
                "silent": False
            },
            "Process3": {
                "execute": True,
                "silent": False
            },
            "Process4": {
                "execute": True,
                "silent": False
            },
            "Process5": {
                "execute": True,
                "silent": False
            }
        }
        assert dict_process == dict_process_ref
        
        if study == "Study1":

            dict_inputs_ref = {
                "parameter1": None,
                "parameter2": None,
                "parameter3": None,
                "parameter4": None,
                "parameter5": None,
                "input2": None,
                "input3.txt": None,
                "input1.txt": {}
            }
            
            list_params = ["parameter6"]
            df_inputs_ref = pd.DataFrame(columns=["ID"] + list_params + ["EXECUTE"])
            
            assert dict_inputs == dict_inputs_ref
            pdt.assert_frame_equal(df_inputs, df_inputs_ref)

            dict_inputs["parameter1"] = 5.9
            dict_inputs["parameter2"] = 14
            dict_inputs["parameter3"] = "Hello"
            dict_inputs["parameter4"] = 18.2
            dict_inputs["parameter5"] = True

            input2_dir = inputs_dir / "input2"
            input2_dir.mkdir(
                exist_ok=True,
                parents=True,
            )

            input3_txt = inputs_dir / "input3.txt"
            with open(input3_txt, "w") as f:
                f.write("")

        if study == "Study2":
            
            dict_inputs_ref = {
                "parameter1": None,
                "parameter2": None,
                "parameter3": None,
                "parameter6": None,
                "input1.txt": None,
                "input2": {},
                "input3.txt": {}
            }
            
            list_params = ["parameter4", "parameter5"]
            df_inputs_ref = pd.DataFrame(columns=["ID"] + list_params + ["EXECUTE"])
            
            assert dict_inputs == dict_inputs_ref
            pdt.assert_frame_equal(df_inputs, df_inputs_ref)

            dict_inputs["parameter1"] = 21.5
            dict_inputs["parameter2"] = 7
            dict_inputs["parameter3"] = "World"
            dict_inputs["parameter6"] = 68.4

            input1_txt = inputs_dir / "input1.txt"
            with open(input1_txt, "w") as f:
                f.write("")

        with open(inputs_json, "w") as f:
            json.dump(dict_inputs, f, indent=4)
        
        df_inputs.loc[len(df_inputs)] = {"ID": "Test1"}
        df_inputs.loc[len(df_inputs)] = {"ID": "Test2"}
        df_inputs.loc[len(df_inputs)] = {"ID": "Test3"}
        df_inputs.set_index("ID", inplace=True)
        df_inputs.to_csv(
            path_or_buf=inputs_csv,
        )


def test_state_define_datasets(
    shared_tmp_path: Path,
    test_config: list[dict[str, Any]],
) -> None:

    workflow = test_config
    
    with pytest.raises(SystemExit) as exc_info:
        app = Application(
            app_name=APP_NAME,
            config_path=shared_tmp_path,
            workflow=workflow,
        )
        app.configure()
        app.settings()
        assert exc_info.value.code == 1
    
    for study in ["Study1", "Study2"]:

        study_dir: Path = shared_tmp_path / APP_NAME / study
        inputs_dir: Path = study_dir / "0_inputs"
        datasets_dir: Path = inputs_dir / "0_datasets"
        inputs_csv: Path = study_dir / "inputs.csv"

        df_inputs = pd.read_csv(
            filepath_or_buffer=inputs_csv,
            index_col=0,
        )
        for idx in df_inputs.index:

            dataset_dir: Path = datasets_dir / idx
            assert dataset_dir.is_dir()

            if study == "Study1":

                input1_txt = dataset_dir / "input1.txt"
                with open(input1_txt, "w") as f:
                    f.write("")
            
            if study == "Study2":

                input2_dir = dataset_dir / "input2"
                input2_dir.mkdir(
                    exist_ok=True,
                    parents=True,
                )

                input3_txt = dataset_dir / "input3.txt"
                with open(input3_txt, "w") as f:
                    f.write("")

        if study == "Study1":

            df_inputs.loc["Test1", "parameter6"] = 61.2
            df_inputs.loc["Test2", "parameter6"] = 57.9
            df_inputs.loc["Test3", "parameter6"] = 54.1

        if study == "Study2":

            df_inputs.loc["Test1", "parameter4"] = 17.4
            df_inputs.loc["Test2", "parameter4"] = 19.3
            df_inputs.loc["Test3", "parameter4"] = 16.8

            df_inputs["parameter5"] = df_inputs["parameter5"].astype("boolean")
            df_inputs.loc["Test1", "parameter5"] = False
            df_inputs.loc["Test2", "parameter5"] = False
            df_inputs.loc["Test3", "parameter5"] = True
        
        df_inputs.to_csv(
            path_or_buf=inputs_csv,
        )


def test_state_run(
    shared_tmp_path: Path,
    test_config: list[dict[str, Any]],
) -> None:

    workflow = test_config
    
    app = Application(
        app_name=APP_NAME,
        config_path=shared_tmp_path,
        workflow=workflow,
    )
    app.configure()
    app.settings()
    app()

    dict_outputs = {}
    list_processes = []
    for i, proc in enumerate(workflow):
        
        dir_name = f"{i + 1}_{proc['process'].__name__}"
        list_processes.append(dir_name)
        
        dict_outputs[dir_name] = []
        if "output_paths" in proc:
            for _, value in proc["output_paths"].items():
                dict_outputs[dir_name].append(value)

    for study in ["Study1", "Study2"]:

        study_dir: Path = shared_tmp_path / APP_NAME / study
        
        analysis_json: Path = study_dir / "analysis.json"
        assert analysis_json.is_file()

        diagram_json: Path = study_dir / ".diagram.json"
        assert diagram_json.is_file()

        paths_json: Path = study_dir / ".paths.json"
        assert paths_json.is_file()

        inputs_csv: Path = study_dir / "inputs.csv"
        df_inputs = pd.read_csv(
            filepath_or_buffer=inputs_csv,
            index_col=0,
        )

        with open(analysis_json) as f:
            dict_analysis: dict = json.load(f)
        with open(diagram_json) as f:
            dict_diagram: dict = json.load(f)
        with open(paths_json) as f:
            dict_paths: dict = json.load(f)
        
        for proc in list_processes:
            
            proc_dir: Path = study_dir / proc
            assert proc_dir.is_dir()

            if study == "Study1":
                list_proc_no_dataset = ["5_Process5"]
            if study == "Study2":
                list_proc_no_dataset = ["1_Process1", "5_Process5"]

            if proc not in list_proc_no_dataset:
                for idx in df_inputs.index:
                    dataset_dir: Path = proc_dir / idx
                    assert dataset_dir.is_dir()
                    for out in dict_outputs[proc]:
                        out_path: Path = dataset_dir / out
                        if len(out.split(".")) > 1:
                            assert out_path.is_file()
                        else:
                            assert out_path.is_dir()
            else:
                for out in dict_outputs[proc]:
                    out_path: Path = proc_dir / out
                    if len(out.split(".")) > 1:
                        assert out_path.is_file()
                    else:
                        assert out_path.is_dir()

        dict_diagram_ref = {
            "Process1": {
                "params": [
                    "parameter1",
                    "parameter2",
                    "parameter3"
                ],
                "allparams": [
                    "parameter1",
                    "parameter2",
                    "parameter3"
                ],
                "paths": [
                    "input1.txt"
                ],
                "allpaths": [
                    "input1.txt"
                ],
                "required_paths": [],
                "output_paths": [
                    "output1.txt"
                ]
            },
            "Process2": {
                "params": [],
                "allparams": [
                    "parameter1",
                    "parameter2",
                    "parameter3"
                ],
                "paths": [
                    "input1.txt",
                    "input2"
                ],
                "allpaths": [
                    "input1.txt",
                    "input2"
                ],
                "required_paths": [
                    "output1.txt"
                ],
                "output_paths": [
                    "output2.txt"
                ]
            },
            "Process3": {
                "params": [
                    "parameter2",
                    "parameter4",
                    "parameter5"
                ],
                "allparams": [
                    "parameter2",
                    "parameter4",
                    "parameter5",
                    "parameter1",
                    "parameter3"
                ],
                "paths": [],
                "allpaths": [
                    "input1.txt",
                    "input2"
                ],
                "required_paths": [
                    "output2.txt"
                ],
                "output_paths": [
                    "output3.txt",
                    "output4.txt"
                ]
            },
            "Process4": {
                "params": [
                    "parameter3",
                    "parameter6"
                ],
                "allparams": [
                    "parameter3",
                    "parameter6",
                    "parameter2",
                    "parameter4",
                    "parameter5",
                    "parameter1"
                ],
                "paths": [
                    "input3.txt"
                ],
                "allpaths": [
                    "input3.txt",
                    "input1.txt",
                    "input2"
                ],
                "required_paths": [
                    "output3.txt",
                    "output4.txt"
                ],
                "output_paths": [
                    "output5"
                ]
            },
            "Process5": {
                "params": [],
                "allparams": [],
                "paths": [],
                "allpaths": [],
                "required_paths": [],
                "output_paths": [
                    "output6.txt"
                ]
            }
        }
        assert dict_diagram == dict_diagram_ref

        if study == "Study1":

            dict_analysis_ref = {
                "Process5": {
                    "Test1": {
                        "setting1": False,
                        "setting2": 5,
                        "setting3": "Label"
                    },
                    "Test2": {
                        "setting1": False,
                        "setting2": 5,
                        "setting3": "Label"
                    },
                    "Test3": {
                        "setting1": False,
                        "setting2": 5,
                        "setting3": "Label"
                    }
                },
            }

            dict_paths_ref = {
                "output1.txt": {
                    "Test1": str(study_dir / "1_Process1/Test1/output1.txt"),
                    "Test2": str(study_dir / "1_Process1/Test2/output1.txt"),
                    "Test3": str(study_dir / "1_Process1/Test3/output1.txt"),
                },
                "output2.txt": {
                    "Test1": str(study_dir / "2_Process2/Test1/output2.txt"),
                    "Test2": str(study_dir / "2_Process2/Test2/output2.txt"),
                    "Test3": str(study_dir / "2_Process2/Test3/output2.txt"),
                },
                "output3.txt": {
                    "Test1": str(study_dir / "3_Process3/Test1/output3.txt"),
                    "Test2": str(study_dir / "3_Process3/Test2/output3.txt"),
                    "Test3": str(study_dir / "3_Process3/Test3/output3.txt"),
                },
                "output4.txt": {
                    "Test1": str(study_dir / "3_Process3/Test1/output4.txt"),
                    "Test2": str(study_dir / "3_Process3/Test2/output4.txt"),
                    "Test3": str(study_dir / "3_Process3/Test3/output4.txt"),
                },
                "output5": {
                    "Test1": str(study_dir / "4_Process4/Test1/output5"),
                    "Test2": str(study_dir / "4_Process4/Test2/output5"),
                    "Test3": str(study_dir / "4_Process4/Test3/output5"),
                },
                "output6.txt": str(study_dir / "5_Process5/output6.txt"),
            }
        
        if study == "Study2":

            dict_analysis_ref = {
                "Process5": {
                    "Test1": {
                        "setting1": False,
                        "setting2": 5,
                        "setting3": "Label"
                    },
                    "Test2": {
                        "setting1": False,
                        "setting2": 5,
                        "setting3": "Label"
                    },
                    "Test3": {
                        "setting1": False,
                        "setting2": 5,
                        "setting3": "Label"
                    }
                },
            }

            dict_paths_ref = {
                "output1.txt": str(study_dir / "1_Process1/output1.txt"),
                "output2.txt": {
                    "Test1": str(study_dir / "2_Process2/Test1/output2.txt"),
                    "Test2": str(study_dir / "2_Process2/Test2/output2.txt"),
                    "Test3": str(study_dir / "2_Process2/Test3/output2.txt"),
                },
                "output3.txt": {
                    "Test1": str(study_dir / "3_Process3/Test1/output3.txt"),
                    "Test2": str(study_dir / "3_Process3/Test2/output3.txt"),
                    "Test3": str(study_dir / "3_Process3/Test3/output3.txt"),
                },
                "output4.txt": {
                    "Test1": str(study_dir / "3_Process3/Test1/output4.txt"),
                    "Test2": str(study_dir / "3_Process3/Test2/output4.txt"),
                    "Test3": str(study_dir / "3_Process3/Test3/output4.txt"),
                },
                "output5": {
                    "Test1": str(study_dir / "4_Process4/Test1/output5"),
                    "Test2": str(study_dir / "4_Process4/Test2/output5"),
                    "Test3": str(study_dir / "4_Process4/Test3/output5"),
                },
                "output6.txt": str(study_dir / "5_Process5/output6.txt"),
            }
        
        assert dict_analysis == dict_analysis_ref
        assert dict_paths == dict_paths_ref