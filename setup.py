from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="alleycat-ui",
    version="0.0.2",
    author="Xavier Cho",
    author_email="mysticfallband@gmail.com",
    description="Lightweight GUI widget toolkit for UPBGE (Uchronia Project Blender Game Engine).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mysticfall/alleycat-ui",
    packages=find_packages(),
    install_requires=["alleycat-reactive==0.4.3", "returns==0.15.0", "rx==3.1.1", "pangocairocffi==0.5.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)
