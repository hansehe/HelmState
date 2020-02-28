FROM python:3.6

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN python -m unittest discover -p *Test*.py