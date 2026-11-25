from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def test_try_repo(tmp_path):
    # pre-commit relpaths the repo against cwd, which fails across Windows drives
    with tempfile.TemporaryDirectory(dir=REPO_ROOT) as d:
        target = Path(d)
        (target / "good.py").write_text("x: int = 1\n")
        (target / "bad.py").write_text('x: int = "a"\n')
        subprocess.check_call(("git", "init", "-q", str(target)))
        subprocess.check_call(("git", "-C", str(target), "add", "good.py", "bad.py"))

        proc = subprocess.run(
            (
                sys.executable,
                "-m",
                "pre_commit",
                "try-repo",
                str(REPO_ROOT),
                "pyright",
                "--all-files",
            ),
            check=False,
            cwd=target,
            env={**os.environ, "PRE_COMMIT_HOME": str(tmp_path / "pre-commit-home")},
            capture_output=True,
            text=True,
        )
    output = proc.stdout + proc.stderr

    assert proc.returncode == 1, output
    assert "bad.py:1:10 - error" in output
    assert "good.py:" not in output
    assert "1 error, 0 warnings" in output
