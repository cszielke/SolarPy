from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent

setup(
    name="solarpy",
    version="0.2.1",
    description="Data collection and interfaces for a photovoltaic system",
    long_description=(ROOT / "readme.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    py_modules=["SolarPy"],
    python_requires=">=3.11",
    install_requires=[
        "requests==2.33.0",
        "pytz==2025.2",
        "influxdb==5.3.2",
        "influxdb-client==1.48.0",
        "paho-mqtt<2.0.0",
        "pyserial==3.5",
        "jsons==1.6.3",
        "PyMySQL==1.1.1",
        "pymodbus==3.9.2",
        "pillow==12.3.0",
        "psutil==7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "solarpy=SolarPy:main",
        ],
    },
    license_files=["LICENSE"],
)
