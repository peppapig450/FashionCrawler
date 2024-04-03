from pathlib import Path

import tomlkit


def parse_packages_from_poetry(poetry_lock_file: Path):
    packages = []
    with open(poetry_lock_file, "r", encoding="utf-8") as file:
        toml_content = file.read()
        parsed_toml = tomlkit.parse(toml_content)

        for package in parsed_toml["package"]:  # type: ignore
            package_name = package["name"]
            package_version = package["version"]
            packages.append((f"{package_name}=={package_version}"))

    return packages


def write_to_requirements_txt(package_strings, requirements_txt_file: Path):
    with open(requirements_txt_file, "w", encoding="utf-8") as file:
        for package in package_strings:
            file.write(package)


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent.parent
    poetry_lock_file = script_dir.parent / "poetry.lock"
    package_strings = parse_packages_from_poetry(poetry_lock_file)

    requirements_txt_file = script_dir.parent / "requirements.txt"
    write_to_requirements_txt(package_strings, requirements_txt_file)
