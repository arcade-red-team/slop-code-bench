"""Pick the fixed 8-problem pilot subset: random.Random(SEED).sample(sorted(problems), K)."""

import random
import sys
from pathlib import Path

SEED = 2603
K = 8


def problems(root: Path) -> list[str]:
    return sorted(p.parent.name for p in root.glob("*/config.yaml"))


def checkpoints(root: Path, name: str) -> int:
    return len(list((root / name).glob("checkpoint_*.md")))


if __name__ == "__main__":
    root = Path(sys.argv[1])
    names = problems(root)
    assert len(names) == 36, f"expected 36 problems in v2, found {len(names)}"
    picked = sorted(random.Random(SEED).sample(names, K))
    for name in picked:
        print(name, checkpoints(root, name))
    print("total_checkpoints", sum(checkpoints(root, n) for n in picked))
