"""
Invoke tasks for easy project automation.
"""

from pathlib import Path

from invoke import task

PROJECT_ROOT = Path(__file__).parent.resolve()


@task
def style(c):
    """
    Runs style checking and linting tools on the project.
    """
    c.run("isort .")
    c.run("flake8 .")
    c.run("black .")
    c.run("mypy .")
