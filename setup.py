# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    project_license = f.read()

setup(
    name="AvailabilityTrackingBot",
    version="0.0.1",
    author="Harry Di",
    author_email="horrydee47@gmail.com",
    description="Selenium-based web crawler to check the availability of bookings",
    license=project_license,
    keywords="Bot",
    url="https://github.com/hdrive99/AvailabilityTrackingBot",
    long_description=readme,
    classifiers=[],
    packages=find_packages(),
    install_requires=["selenium", "webdriver-manager", "undetected-chromedriver", "psutil"]
)
