from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def test_try_repo(tmp_path, subtests):
    target = tmp_path / "target"
    target.mkdir()
    (target / "good.py").write_text("x: int = 1\n")
    (target / "bad.py").write_text('x: int = "a"\n')
    subprocess.check_call(("git", "init", "-q", str(target)))
    subprocess.check_call(("git", "-C", str(target), "add", "."))

    # one try-repo run for all cases: each run builds a fresh shadow commit, so the hook env is never reused across runs
    env = {**os.environ, "PRE_COMMIT_HOME": str(tmp_path / "pre-commit-home")}
    proc = subprocess.run((sys.executable, "-m", "pre_commit", "try-repo", str(REPO_ROOT), "pyright", "--all-files"), cwd=target, env=env, capture_output=True, text=True)
    output = proc.stdout + proc.stderr

    with subtests.test("exit code"):
        assert proc.returncode == 1, output
    with subtests.test("bad file reported"):
        assert "bad.py:1:10 - error" in output
    with subtests.test("good file clean"):
        assert "good.py:" not in output
    with subtests.test("summary"):
        assert "1 error, 0 warnings" in output
