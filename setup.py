from pathlib import Path

from setuptools import find_packages, setup

SELF_PATH = Path(__file__).parent.absolute()


def read(path: Path):
    with open(path, "r") as f:
        return f.read()


setup(
    name="recipe_planner",
    description="An excel spreadsheet for smart planning lunches for the week",
    entry_points={
        "console_scripts": ["recipe_planner=recipe_planner.cli:app"],
    },
    author="Nicolas Garcia Cavalcante",
    author_email="nicolasgcavalcante@gmail.com",
    packages=find_packages(include=["recipe_planner", "recipe_planner.*"]),
    include_package_data=True,
    license="MIT license",
    keywords="recipe_planner",
    url="https://github.com/nicolasCavalcante/recipe_planner",
    long_description=read(SELF_PATH / "README.md"),
)
