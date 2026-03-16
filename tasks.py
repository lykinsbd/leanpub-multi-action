"""Tasks for use with Invoke."""

import os
import pathlib
import sys

import invoke.exceptions
from invoke import task

try:
    import toml
except ImportError:
    sys.exit("Please make sure to `pip install toml` or enable the virtual environment.")


PYPROJECT_CONFIG = toml.load("pyproject.toml")
PROJECT_CONFIG = PYPROJECT_CONFIG["project"]

# Can be set to a separate Python version to be used for launching or building image
INVOKE_PYTHON_VER = os.getenv("INVOKE_PYTHON_VER", "3.9")
# Name of the docker image/image
IMAGE_NAME = os.getenv("IMAGE_NAME", PROJECT_CONFIG["name"])
# Tag for the image
IMAGE_VER = os.getenv("IMAGE_VER", f"{PROJECT_CONFIG['version']}")
# Leanpub API Key for testing
LEANPUB_API_KEY = os.getenv("LEANPUB_API_KEY", "test_api_key!")
# Leanpub Book Slug for testing
LEANPUB_BOOK_SLUG = os.getenv("LEANPUB_BOOK_SLUG", "test_book_slug")

# Gather current working directory for Docker commands
PWD = os.getcwd()


def run_cmd(
    context,
    exec_cmd,
    pty=True,
    hide=False,
    error_message="An unknown error has occurred!",
):
    """Run the invoke task command.

    Args:
        context ([invoke.task]): Invoke task object.
        exec_cmd ([str]): Command to run.
        pty ([bool]): Run command in a pty (default True)
        hide ([bool]): Suppress output from command to run (default False)
        error_message ([str]): Error message to print if an error occurs running this command.

    Returns:
        result (obj): Contains Invoke result from running task.

    """
    print(f"LOCAL - Running command {exec_cmd}")
    result = context.run(exec_cmd, pty=pty, hide=hide, warn=True)
    if not result:
        print(f"ERROR - {error_message}\n{result.stdout if pty else result.stderr}")
        raise invoke.exceptions.UnexpectedExit(result)

    return result


@task(
    help={
        "cache": "Whether to use Docker's cache when building images (default enabled)",
        "force_rm": "Always remove intermediate images",
        "hide": "Suppress output from Docker",
    }
)
def build(context, cache=True, force_rm=False, hide=False):
    """Build the Python package and Docker image."""
    python_name = f"{IMAGE_NAME}-{IMAGE_VER}"
    docker_name = f"{IMAGE_NAME}:{IMAGE_VER}"

    print(f"Building Python package {python_name}")
    run_cmd(
        context=context,
        exec_cmd="uv build",
        pty=False,
        error_message=f"Failed to build Python package {python_name}",
    )

    print(f"Building Docker image {docker_name}")
    command = f"docker build --tag {docker_name} -f Dockerfile ."

    if not cache:
        command += " --no-cache"
    if force_rm:
        command += " --force-rm"

    run_cmd(
        context=context,
        exec_cmd=command,
        pty=False,
        hide=hide,
        error_message=f"Failed to build Docker image {docker_name}",
    )


@task
def clean(context):
    """Remove the project specific image."""
    print(f"Attempting to forcefully remove image {IMAGE_NAME}:{IMAGE_VER}")
    context.run(f"docker rmi {IMAGE_NAME}:{IMAGE_VER} --force")
    print(f"Successfully removed image {IMAGE_NAME}:{IMAGE_VER}")


@task
def rebuild(context):
    """Clean the Docker image and then rebuild without using cache."""
    clean(context)
    build(context, cache=False)


@task
def pytest(context):
    """Run pytest test cases."""
    exec_cmd = "pytest"
    run_cmd(context, exec_cmd)


@task
def ruff(context):
    """Run ruff linter and formatter checks."""
    run_cmd(context, "ruff check .")
    run_cmd(context, "ruff format --check .")


@task
def pylint(context):
    """Run pylint code analysis."""
    exec_cmd = 'find . -name "*.py" | xargs pylint'
    run_cmd(context, exec_cmd)


@task
def yamllint(context):
    """Run yamllint to validate formatting adheres to NTC defined YAML standards."""
    exec_cmd = "yamllint ."
    run_cmd(context, exec_cmd)


@task
def tests(context):
    """Run all tests for this repository."""
    ruff(context)
    pylint(context)
    yamllint(context)
    pytest(context)

    print("All tests have passed!")


@task(
    help={
        "patch": "Semvar patch version bump, i.e. v0.0.1 to v0.0.2",
        "minor": "Semvar minor version bump, i.e. v0.0.1 to v0.1.0",
        "major": "Semvar major version bump, i.e. v0.0.1 to v1.0.0",
    }
)
def pre_release(context, patch=False, minor=False, major=False):
    """Pre-release actions."""
    bump_type = ""
    if patch:
        bump_type = "patch"
    elif minor:
        bump_type = "minor"
    elif major:
        bump_type = "major"

    # Check if more than one type was specified (or none)
    if not patch and not minor and not major:
        raise invoke.exceptions.Exit("You must specify a patch/minor/major version bump!")
    if patch and (minor or major):
        raise invoke.exceptions.Exit("You must only specify ONE of patch/minor/major!")
    if minor and (patch or major):
        raise invoke.exceptions.Exit("You must only specify ONE of patch/minor/major!")

    print("Checking Git status")
    run_cmd(
        context,
        exec_cmd="git diff --exit-code --name-status",
        pty=False,
        error_message="There are uncommitted changes, please commit or stash these files.",
    )

    print("Checking for Newsfragments")
    run_cmd(
        context,
        exec_cmd="towncrier check --compare-with origin/main",
        pty=False,
        error_message=(
            "There are committed changes, but no Newsfragments!\n"
            "Please use `towncrier create <issuenum>.<type>` and summarize your changes in the resultant file."
        ),
    )

    # Compute new version
    current_ver = PROJECT_CONFIG["version"]
    parts = current_ver.split(".")
    if bump_type == "patch":
        parts[2] = str(int(parts[2]) + 1)
    elif bump_type == "minor":
        parts[1] = str(int(parts[1]) + 1)
        parts[2] = "0"
    elif bump_type == "major":
        parts[0] = str(int(parts[0]) + 1)
        parts[1] = "0"
        parts[2] = "0"
    new_image_ver = ".".join(parts)

    print(f"Starting pre-release actions to perform a {bump_type} version bump on {IMAGE_NAME}:{IMAGE_VER}")

    # Update version in pyproject.toml
    pyproject = pathlib.Path("pyproject.toml")
    pyproject.write_text(
        pyproject.read_text(encoding="utf8").replace(f'version = "{current_ver}"', f'version = "{new_image_ver}"'),
        encoding="utf8",
    )
    print(f"Project now at {IMAGE_NAME}:{new_image_ver}")

    print("Copying existing Release Notes to Changelog")
    changelog = pathlib.Path("CHANGELOG.rst")
    current_changelog = changelog.read_text(encoding="utf8")
    changelog.write_text(
        pathlib.Path(PYPROJECT_CONFIG["tool"]["towncrier"]["filename"]).read_text(encoding="utf8")
        + "\n\n"
        + current_changelog,
        encoding="utf8",
    )

    print("Creating updated Release Notes")
    run_cmd(
        context,
        exec_cmd=f"towncrier build --yes --version={new_image_ver}",
        pty=False,
        error_message="Unable to create new release notes!",
    )

    print("Updating example in README.md")
    readme = pathlib.Path("README.md")
    readme.write_text(
        readme.read_text(encoding="utf8").replace(f"v{IMAGE_VER}", f"v{new_image_ver}"),
        encoding="utf8",
    )

    print("Committing the changes and pushing to origin.")
    run_cmd(
        context,
        exec_cmd=f"git commit --all --message 'Pre-release prep for {new_image_ver}'",
        pty=False,
        error_message="Unable to stage and commit changes!",
    )

    run_cmd(
        context,
        exec_cmd="git push",
        pty=False,
        error_message="Unable to push committed changes!",
    )

    print(
        "\nNOTE - To finish the release process you will need to:\n"
        "\t1: Open a PR and merge these changes into `main`\n"
        "\t2: Run `invoke release` from the uv shell"
    )


@task
def release(context):
    """Start a Release on GitHub."""
    print(f"Starting a release of v{IMAGE_VER} on GitHub!")
    run_cmd(
        context,
        exec_cmd="git checkout main",
        pty=False,
        error_message="Failed to checkout main!",
    )

    run_cmd(
        context,
        exec_cmd="git pull origin main",
        pty=False,
        error_message="Failed to pull from origin/main",
    )

    run_cmd(
        context,
        exec_cmd=f"git tag v{IMAGE_VER}",
        pty=False,
        error_message=f"Failed to create the tag 'v{IMAGE_VER}'!",
    )

    run_cmd(
        context,
        exec_cmd="git push --tags",
        pty=False,
        error_message=f"Failed to push the tag 'v{IMAGE_VER}'!",
    )
