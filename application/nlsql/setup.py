from setuptools import setup, find_packages

setup(
    name="nlsql",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.2",
        "python-multipart>=0.0.5",
        "aiofiles>=0.7.0",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "python-dotenv>=0.19.0",
        "openai>=0.27.0"
    ],
    python_requires=">=3.9",
)
