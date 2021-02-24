from setuptools import setup, find_packages
import rndt


def read_file(path: str):
    with open(path, "r") as file:
        return file.read()


setup_requires = [
    "wheel",
]

setup(
    name="rndt",
    version=rndt.__version__,
    url=rndt.__url__,
    description=rndt.__doc__,
    long_description=read_file("README.md"),
    author=rndt.__author__,
    author_email=rndt.__email__,
    license=rndt.__license__,
    platforms="any",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    packages=find_packages(),
    package_data={'':['*.html', '*.js']},
    include_package_data=True,
    install_requires=read_file("requirements.txt").splitlines(),
)
