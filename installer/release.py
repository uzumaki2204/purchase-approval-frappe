#!/usr/bin/env python3
"""Build the purchase_approval Git repository snapshot and publish to GitHub."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/uzumaki2204/purchase-approval-frappe.git"
MESSAGES = json.loads((ROOT / "installer" / "release_messages.json").read_text(encoding="utf-8"))
EXCLUDED_NAMES = {".git", ".venv", "__pycache__", "build", "dist", "purchase_approval.egg-info"}


def run(*args: str, cwd: Path | None = None, stdout=None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        stdout=stdout or subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=stdout is None,
    )
    return result.stdout.strip() if stdout is None else ""


def copy_source(destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        ignored = {name for name in names if name in EXCLUDED_NAMES}
        ignored.update(name for name in names if name.endswith((".pyc", ".pyo")))
        return ignored

    shutil.copytree(ROOT, destination, ignore=ignore, dirs_exist_ok=True)
    for shell_script in destination.rglob("*.sh"):
        contents = shell_script.read_bytes()
        normalized = contents.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if normalized != contents:
            shell_script.write_bytes(normalized)


def clear_checkout(repo: Path) -> None:
    for entry in repo.iterdir():
        if entry.name == ".git":
            continue
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--publish",
        action="store_true",
        help="push the release tag, main, and supported Frappe version branch to the public GitHub repo",
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()

    language = os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG", "en")
    message_language = "vi" if language.startswith("vi") else "en"

    def msg(key: str, **values: str) -> str:
        return MESSAGES[message_language][key].format(**values)

    with (ROOT / "pyproject.toml").open("rb") as stream:
        app_version = tomllib.load(stream)["project"]["version"]
    manifest_path = ROOT / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    frappe_branch = manifest.get("branch", "version-16")
    if not re.fullmatch(r"version-\d+", frappe_branch):
        raise SystemExit(msg("invalid_frappe_branch"))

    app_init = (ROOT / "purchase_approval" / "__init__.py").read_text(encoding="utf-8")
    version_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', app_init, re.MULTILINE)
    manifest_version = manifest.get("version") or manifest.get("app_version")
    if not version_match or manifest_version != app_version or version_match.group(1) != app_version:
        raise SystemExit(msg("version_mismatch"))

    tag = f"v{app_version}"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    archive_name = f"purchase-approval-frappe-{tag}.tar.gz"
    archive_path = args.output_dir / archive_name

    with tempfile.TemporaryDirectory(prefix="purchase-approval-release-") as temp:
        repo = Path(temp) / "repo"
        if args.publish:
            run("git", "clone", REPOSITORY_URL, str(repo))
            clear_checkout(repo)
            if subprocess.run(
                ("git", "rev-parse", "--verify", "HEAD"),
                cwd=repo,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode:
                run("git", "symbolic-ref", "HEAD", "refs/heads/main", cwd=repo)
        else:
            repo.mkdir()
            run("git", "init", "--initial-branch=main", cwd=repo)
        copy_source(repo)
        run("git", "config", "user.name", "Purchase Approval Release", cwd=repo)
        run("git", "config", "user.email", "release@localhost", cwd=repo)
        run("git", "config", "core.autocrlf", "false", cwd=repo)
        run("git", "add", "--all", cwd=repo)
        run("git", "commit", "--allow-empty", "-m", f"Release {tag}", cwd=repo)
        commit = run("git", "rev-parse", "HEAD", cwd=repo)
        current_branch = run("git", "branch", "--show-current", cwd=repo)
        if current_branch != frappe_branch:
            if args.publish:
                run("git", "branch", "-f", frappe_branch, commit, cwd=repo)
            else:
                run("git", "branch", frappe_branch, commit, cwd=repo)
        run("git", "tag", "-a", tag, "-m", f"Purchase Approval {tag}", cwd=repo)

        if args.publish:
            run("git", "push", "origin", "HEAD:refs/heads/main", cwd=repo)
            run("git", "push", "origin", f"HEAD:refs/heads/{frappe_branch}", cwd=repo)
            run("git", "push", "origin", f"refs/tags/{tag}", cwd=repo)

        with archive_path.open("wb") as archive:
            run(
                "git",
                "archive",
                "--format=tar.gz",
                f"--prefix=purchase-approval-frappe-{tag}/",
                tag,
                cwd=repo,
                stdout=archive,
            )

    digests = {
        archive_name: hashlib.sha256(archive_path.read_bytes()).hexdigest(),
    }
    (args.output_dir / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in digests.items()),
        encoding="utf-8",
        newline="\n",
    )
    print(msg("tag", tag=tag))
    print(msg("commit", commit=commit))
    print(msg("archive", archive=archive_path))
    print(msg("checksums", path=args.output_dir / "SHA256SUMS"))
    if args.publish:
        print(msg("published", repository=REPOSITORY_URL, branch=frappe_branch, tag=tag))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() if isinstance(error.stderr, str) else ""
        if detail:
            print(detail, file=sys.stderr)
        raise SystemExit(error.returncode)
