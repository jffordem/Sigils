# Sigils
Command-line tool that solves tetramino puzzles found in The Talos Principle.

## Requirements
- [Python 3](https://www.python.org/download)
- [Numpy](https://numpy.org/)

## Usage
C:> sigils.py *rows* *cols* *sigils...*

The sigil shapes are named I, O, T, J, L, S, Z

## Example
C:> sigils.py 5 4 I O T L J

C:> sigils.py 5 4 IOTLJ

## Tkinter version

C:> wsigils.pyw

## Web app (flask) version

C:> set FLASK_APP=app.py

C:> set FLASK_ENV=development

C:> flask run
