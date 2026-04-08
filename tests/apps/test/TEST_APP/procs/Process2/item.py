from pathlib import Path

import attrs

from nuremics import Process


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