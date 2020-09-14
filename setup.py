import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="md-uploader-sergey", # Replace with your own username
    version="0.0.1",
    author="Sergey Pisarenko",
    author_email="sergey@example.com",
    description="Headless NetMD track uploader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pisarenko-net/md-uploader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["libusb1", "pycryptodome", "tinytag", "transliterate"],
    scripts=['md-uploader/md_upload_ctl.py']
)
