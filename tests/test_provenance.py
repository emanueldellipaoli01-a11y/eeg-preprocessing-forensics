import subprocess
from pathlib import Path

from eeg_forensics.provenance import configuration_hash, file_sha256, git_commit


def test_configuration_hash_is_deterministic():
    config = {"b": 2, "a": [1, 2, 3]}
    assert configuration_hash(config) == configuration_hash({"a": [1, 2, 3], "b": 2})


def test_file_sha256(tmp_path: Path):
    path = tmp_path / "input.bin"
    path.write_bytes(b"hello world")
    assert file_sha256(path) == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_git_commit_uses_requested_repository(tmp_path: Path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "file.txt").write_text("ok", encoding="utf-8")
    subprocess.run(["git", "add", "file.txt"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "test"],
        cwd=tmp_path,
        check=True,
    )
    commit = git_commit(tmp_path)
    assert commit is not None
    assert len(commit) == 40
