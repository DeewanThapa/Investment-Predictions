from setuptools import find_packages,setup
from typing import List

def get_requirements()->List[str]:
    """
    This function will return list of requirements
    """
    requirement_list:List[str] = []

    return requirement_list


setup(
    name="Investment",
    version="0.0.1",
    author="Deewan Thapa",
    author_email="karan.thapa37@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)
