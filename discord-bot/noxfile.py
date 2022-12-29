# -*- coding=utf-8 -*-
"""Automated linting, formatting, and typechecking."""
import nox
from nox.sessions import Session


@nox.session(reuse_venv=True)
def format_code(session: Session):
    """Format the codebase."""
    session.install("isort", "-U")
    session.install("black", "-U")

    session.run("isort", "bot")
    session.run("black", "bot")


@nox.session(reuse_venv=True)
def lint_code(session: Session):
    """Lint the codebase."""
    session.install("codespell", "-U")
    session.install("flake8", "-U")
    session.install("-r", "flake8-requirements.txt", "-U")

    session.run("codespell", "bot")
    session.run("flake8", "bot")


@nox.session(reuse_venv=True)
def typecheck_code(session: Session):
    session.install("-r", "requirements.txt", "-U")
    session.install("pyright", "-U")

    session.run("pyright", "bot")
