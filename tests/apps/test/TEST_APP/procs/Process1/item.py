from pathlib import Path

import attrs

from nuremics import Process


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