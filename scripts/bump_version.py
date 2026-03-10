import os
import re
import sys

def bump_version(part_to_bump="patch"):
    pyproject_path = "pyproject.toml"
    if not os.path.exists(pyproject_path):
        print("Error: pyproject.toml not found.")
        sys.exit(1)

    with open(pyproject_path, "r") as f:
        content = f.read()

    # Find the current version
    version_match = re.search(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
    if version_match is None:
        print("Error: Could not parse version from pyproject.toml.")
        sys.exit(1)

    major, minor, patch = map(int, version_match.groups())
    old_version = f"{major}.{minor}.{patch}"

    if part_to_bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif part_to_bump == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    # Replace the version
    new_content = re.sub(
        r'version\s*=\s*"\d+\.\d+\.\d+"',
        f'version = "{new_version}"',
        content,
        count=1
    )

    with open(pyproject_path, "w") as f:
        f.write(new_content)

    print(new_version) # Output the new version to stdout so GitHub Actions can capture it

if __name__ == "__main__":
    bump_type = "patch"
    if len(sys.argv) > 1:
         bump_type = sys.argv[1].lower()
         
    # Extremely basic logic: if commit message (passed by CI) has `feat:` it's a minor bump, `BREAKING CHANGE:` is major
    commit_msg = os.environ.get("COMMIT_MESSAGE", "")
    
    if "BREAKING CHANGE:" in commit_msg:
         bump_type = "major"
    elif "feat:" in commit_msg or "feat(" in commit_msg:
         bump_type = "minor"
         
    bump_version(bump_type)
