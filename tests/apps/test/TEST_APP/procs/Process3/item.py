from pathlib import Path

import attrs

from nuremics import Process


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