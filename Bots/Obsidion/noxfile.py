"""Nox sessions."""
import sys
from pathlib import Path
from textwrap import dedent

import nox
from nox_poetry import Session
from nox_poetry import session


package = "obsidion"
python_versions = ["3.9"]
nox.options.sessions = (
    "pre-commit",
    "safety",
    "mypy",
)


def activate_virtualenv_in_precommit_hooks(session: Session) -> None:
    """Activate virtualenv in hooks installed by pre-commit.

    Args:
        session: The Session object.

    This function patches git hooks installed by pre-commit to activate the
    session's virtual environment. This allows pre-commit to locate hooks in
    that environment when invoked from git.
    """
    if session.bin is None:
        return

    virtualenv = session.env.get("VIRTUAL_ENV")
    if virtualenv is None:
        return

    hookdir = Path(".git") / "hooks"
    if not hookdir.is_dir():
        return

    for hook in hookdir.iterdir():
        if hook.name.endswith(".sample") or not hook.is_file():
            continue

        text = hook.read_text()
        bindir = repr(session.bin)[1:-1]  # strip quotes
        if not (
            Path("A") == Path("a") and bindir.lower() in text.lower() or bindir in text
        ):
            continue

        lines = text.splitlines()
        if not (lines[0].startswith("#!") and "python" in lines[0].lower()):
            continue

        header = dedent(
            f"""\
            import os
            os.environ["VIRTUAL_ENV"] = {virtualenv!r}
            os.environ["PATH"] = os.pathsep.join((
                {session.bin!r},
                os.environ.get("PATH", ""),
            ))
            """
        )

        lines.insert(1, header)
        hook.write_text("\n".join(lines))


@session(name="pre-commit", python="3.9")
def precommit(session: Session) -> None:
    """Lint using pre-commit.

    Args:
        session: The Session object.
    """
    args = session.posargs or ["run", "--all-files"]
    session.install(
        "black",
        "flake8",
        "flake8-bugbear",
        "pep8-naming",
        "flake8-builtins",
        "flake8-bandit",
        "flake8-eradicate",
        "flake8-comprehensions",
        "flake8-import-order",
        "pre-commit",
        "pre-commit-hooks",
        "reorder-python-imports",
    )
    session.run("pre-commit", *args)
    if args and args[0] == "install":
        activate_virtualenv_in_precommit_hooks(session)


@session(python="3.9")
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = session.poetry.export_requirements()
    session.install("safety")
    session.run("safety", "check", f"--file={requirements}", "--bare", "--ignore=36546")


@session(python=python_versions)
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or ["obsidion"]
    session.install(".")
    session.install("mypy", "pytest")
    session.run("mypy", *args)
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")
