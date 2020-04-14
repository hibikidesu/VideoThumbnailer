from setuptools import setup

setup(
    name="videothumbnailer",
    version="1.1",
    description="Creates x amount of thumbnails based video length",
    author="Hibiki",
    py_modules=["videothumbnailer"],
    entry_points={
        "console_scripts": "videothumbnailer=videothumbnailer:main"
    }
)
