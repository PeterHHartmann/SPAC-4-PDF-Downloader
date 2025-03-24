# SPAC-4-PDF-Downloader

A CLI tool for downloading rapport PDF files in bulk

This project is developed using 
[Python](https://www.python.org/)

## Features

## Requirements
 - [Python::3.12](https://www.python.org/downloads/release/python-3120/)

## Installation

Firstly, create a new python virtual environment:
```sh
python3 -m venv .venv
```
and start the environment
```sh
- Unix/macos
source .venv/bin/activate

- Windows (PowerShell)
.venv\Scripts\activate.ps1

- Windows (cmd.exe)
.venv\Scripts\activate.bat
```

Next up, install the necessary requirements:
```sh
pip install -r requirements.txt
```

You are now ready to run the project. To do so use the following:  
```sh
python src/main.py --limit 10
```
IMPORTANT: To not overload the network your on keep the limit of downloads low by using the --limit option in the command.