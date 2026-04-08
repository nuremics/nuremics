from pathlib import Path

import attrs

from nuremics import Process


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