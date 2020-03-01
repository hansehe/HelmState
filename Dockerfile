FROM python:3.6

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN git config --global user.email "test@example.com"
RUN git config --global user.name "test user"

COPY . .

RUN python -m unittest discover -p *Test*.py