import tomllib
from pathlib import Path


def load_project_metadata():
    """Load project metadata from pyproject.toml with fallback values."""
    try:
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        project = data["project"]
        return {
            "title": project["name"].replace("-", " ").title(),
            "description": project["description"],
            "version": project["version"],
        }
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        # Fallback values
        return {
            "title": "Integration Sandbox",
            "description": "API for integration sandbox services",
            "version": "1.0.0",
        }