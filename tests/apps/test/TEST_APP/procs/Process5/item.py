from pathlib import Path

import attrs

from nuremics import Process


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