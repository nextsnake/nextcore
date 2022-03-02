from pathlib import Path


def test_licenses():
    """
    Test that all files have the right license header.
    """
    with open("tests/license_header.txt") as f:
        license_header = f.read()

    source_path = Path("nextcore/")
    failures = 0

    for path in source_path.rglob("*.py"):
        with open(path) as f:
            file_contents = f.read()
            if not file_contents.startswith(license_header):
                print(f"{path} is missing the license header.")
                failures += 1
    
    assert failures == 0, "Some files are missing the license header."
