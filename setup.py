from setuptools import setup, find_packages

setup(
    name="curb_sign_parser",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
)
