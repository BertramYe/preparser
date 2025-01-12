
from os import path
from setuptools import setup, find_packages
# import sys
# sys.path.insert(0, path.abspath(path.dirname(__file__)))
# from InstallHelper import PreInstaller


# get current setup.py absulute path
here = path.abspath(path.dirname(__file__))

# read the content of the README.md files
with open(path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()



setup(
    name="preparser",  # packages name
    author="BertramYe",  # author name
    author_email="bertramyerik@gmail.com",  # author's email
    version="2.0.5",  # pakage version
    description="a slight preparser to help parse webpage content or get request from urls,which supports win, mac and unix.",  # short description
    long_description=long_description,  # get descrition from README.md
    long_description_content_type="text/markdown",  
    keywords=['preparser','parser','parse','crawl', 'webpage','html','api','requests','BeautifulSoup4','BeautifulSoup4','python3','windows','mac','linux'],  # search key words
    # package_dir={"":"preparser"},
    # packages = find_packages(where="preparser"),  # auto findout the pakage
    packages = find_packages(),  # auto findout the pakage
    install_requires=[  # reliable package
        "requests",
        "beautifulsoup4",
        "playwright"  
    ],
    url="https://github.com/BertramYe/preparser",  # project home page
    license="MIT",
    classifiers=[  # package class label, which helps user learn about current package
        "Development Status :: 5 - Production/Stable",   # developed status, reference: https://packaging.python.org/specifications/core-metadata # https://pypi.org/classifiers/
        "Intended Audience :: Developers",      # recomend who use current package
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    # cmdclass={
    #     'PreInstaller': PreInstaller,  # execute the installer when run pip install 
    # },
    python_requires=">=3.9.0",
)
