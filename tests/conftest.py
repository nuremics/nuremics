from pathlib import Path
from typing import Any

import attrs
import pytest

from nuremics import Process


@pytest.fixture(scope="module")
def shared_tmp_path(
    tmp_path_factory: Path
) -> Path:

    return tmp_path_factory.mktemp("app_test")


@pytest.fixture
def test_config() -> list[dict[str, Any]]:
    
    workflow = [
        {
            "process": Process1,
            "user_params": {
                "param1": "parameter1", 
                "param2": "parameter2", 
                "param3": "parameter3",
            },
            "user_paths": {
                "path1": "input1.txt",
            },
            "output_paths": {
                "out1": "output1.txt",
            },
        },
        {
            "process": Process2,
            "hard_params": {
                "param1": 0.887, 
            },
            "user_paths": {
                "path1": "input1.txt",
                "path2": "input2",
            },
            "required_paths": {
                "path3": "output1.txt",
            },
            "output_paths": {
                "out1": "output2.txt",
            },
        },
        {
            "process": Process3,
            "user_params": {
                "param1": "parameter2",
                "param2": "parameter4",
                "param3": "parameter5",
            },
            "required_paths": {
                "path1": "output2.txt",
            },
            "output_paths": {
                "out1": "output3.txt",
                "out2": "output4.txt",
            },
        },
        {
            "process": Process4,
            "user_params": {
                "param1": "parameter3",
                "param2": "parameter6",
            },
            "user_paths": {
                "path1": "input3.txt",
            },
            "required_paths": {
                "path2": "output3.txt",
                "path3": "output4.txt",
            },
            "output_paths": {
                "out1": "output5",
            },
        },
        {
            "process": Process5,
            "overall_analysis": {
                "analysis1": "output5",
            },
            "output_paths": {
                "out1": "output6.txt",
            },
            "settings": {
                "setting1": False,
                "setting2": 5,
                "setting3": "Label",
            },
        },
    ]

    return workflow


@attrs.define
class Process1(Process):

    # Parameters
    param1: float = attrs.field(init=False, metadata={"input": True})
    param2: int = attrs.field(init=False, metadata={"input": True})
    param3: str = attrs.field(init=False, metadata={"input": True})
    
    # Paths
    path1: Path = attrs.field(init=False, metadata={"input": True}, converter=Path)

    # Outputs
    out1: Path = attrs.field(init=False, metadata={"output": True}, converter=Path)

    # Internal
    variable: float = attrs.field(init=False)

    def __call__(self) -> None:
        super().__call__()

        self.operation1()
        self.operation2()
        self.operation3()

    def operation1(self) -> None:
        ...

    def operation2(self) -> None:
        ...

    def operation3(self) -> None:

        file = self.output_paths["out1"]
        with open(file, "w") as f:
            f.write("")


@attrs.define
class Process2(Process):

    # Parameters
    param1: float = attrs.field(init=False, metadata={"input": True})

    # Paths
    path1: Path = attrs.field(init=False, metadata={"input": True}, converter=Path)
    path2: Path = attrs.field(init=False, metadata={"input": True}, converter=Path)
    path3: Path = attrs.field(init=False, metadata={"input": True}, converter=Path)

    # Outputs
    out1: Path = attrs.field(init=False, metadata={"output": True}, converter=Path)

    # Internal
    variable: int = attrs.field(init=False)

    def __call__(self) -> None:
        super().__call__()

        self.operation1()

    def operation1(self) -> None:

        file = self.output_paths["out1"]
        with open(file, "w") as f:
            f.write("")


@attrs.define
class Process3(Process):

    # Parameters
    param1: int = attrs.field(init=False, metadata={"input": True})
    param2: float = attrs.field(init=False, metadata={"input": True})
    param3: bool = attrs.field(init=False, metadata={"input": True})

    # Paths
    path1: Path = attrs.field(init=False, metadata={"input": True}, converter=Path)

    # Outputs
    out1: Path = attrs.field(init=False, metadata={"output": True}, converter=Path)
    out2: Path = attrs.field(init=False, metadata={"output": True}, converter=Path)

    # Internal
    variable: bool = attrs.field(init=False)

    def __call__(self) -> None:
        super().__call__()

        self.operation1()
        self.operation2()
        self.operation3()
        self.operation4()

    def operation1(self) -> None:
        ...

    def operation2(self) -> None:

        file = self.output_paths["out1"]
        with open(file, "w") as f:
            f.write("")

    def operation3(self) -> None:
        ...

    def operation4(self) -> None:
        
        file = self.output_paths["out2"]
        with open(file, "w") as f:
            f.write("")


@attrs.define
class Process4(Process):

    # Parameters
    param1: str = attrs.field(init=False, metadata={"input": True})
    param2: float = attrs.field(init=False, metadata={"input": True})
    
    # Paths
    path1: Path = attrs.field(init=False, metadata={"input": True}, converter=Path)
    path2: Path = attrs.field(init=False, metadata={"input": True}, converter=Path)
    path3: Path = attrs.field(init=False, metadata={"input": True}, converter=Path)

    # Outputs
    out1: Path = attrs.field(init=False, metadata={"output": True}, converter=Path)

    # Internal
    variable: str = attrs.field(init=False)

    def __call__(self) -> None:
        super().__call__()

        self.operation1()
        self.operation2()

    def operation1(self) -> None:
        ...

    def operation2(self) -> None:

        dir = Path(self.output_paths["out1"])
        dir.mkdir(
            exist_ok=True,
            parents=True,
        )


@attrs.define
class Process5(Process):

    # Analysis
    metadata = {
        "input": True,
        "analysis": True,
    }
    analysis1: str = attrs.field(init=False, metadata=metadata)

    # Outputs
    out1: Path = attrs.field(init=False, metadata={"output": True}, converter=Path)

    def __call__(self) -> None:
        super().__call__()

        self.operation1()
    
    def operation1(self) -> None:
        
        file = self.output_paths["out1"]
        with open(file, "w") as f:
            f.write("")