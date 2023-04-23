# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    project_license = f.read()

# Currently works with selenium version 4.8.3, webdriver-manager version 3.8.6, undetected_chromedriver version 3.4.6
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
