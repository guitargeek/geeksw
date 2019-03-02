from setuptools import setup, find_packages

setup(
    name="geeksw",
    version="0.1",
    description="Python analysis framework for CMS",
    long_description="Python package to facilitate analysis work in in the CMS collaboration.",
    url="http://github.com/guitargeek/geeksw",
    author="Jonas Rembser",
    author_email="jonas.rembser@cern.ch",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["numpy",
                      "matplotlib",
                      "awkward",
                      "h5py",
                      "uproot",
                      "uproot-methods"],
)
