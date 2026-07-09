#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate that each plan task declares use cases.")
    parser.add_argument("--plan-path", required=True)
    return parser


def validate(plan_path: Path) -> dict[str, object]:
    resolved = plan_path.expanduser().resolve()
    content = resolved.read_text(encoding="utf-8")
    task_pattern = re.compile(
        r"(?ms)^### Task\s+\d+:.+?(?=^### Task\s+\d+:|^##\s+Proof Oracle|^##\s+Issue Creation Packet|^##\s+Risk Notes|\Z)"
    )
    tasks = list(task_pattern.finditer(content))
    missing: list[str] = []
    for task in tasks:
        text = task.group(0)
        header = text.split("\n", 1)[0].strip()
        use_index = text.find("**Use Cases:**")
        files_index = text.find("**Files:**")
        if use_index < 0 or files_index < 0 or use_index > files_index:
            missing.append(header)
            continue
        use_case_block = text[use_index:files_index]
        if re.search(r"(?m)^-\s+\S", use_case_block) is None:
            missing.append(header)
    return {
        "ok": bool(tasks) and not missing,
        "plan_path": str(resolved),
        "task_count": len(tasks),
        "missing_use_case_count": len(missing),
        "missing_use_case_tasks": missing,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = validate(Path(args.plan_path))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
