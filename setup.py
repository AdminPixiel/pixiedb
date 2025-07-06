from setuptools import setup, find_packages

setup(
    name="pixiedb",
    version="0.1.0",
    description="A lightweight binary NoSQL database inspired by Firebase Firestore, but not affiliated with or endorsed by Google.",
    author="Admin Pixiel",
    packages=find_packages(),
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)