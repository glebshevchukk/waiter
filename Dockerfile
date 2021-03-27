FROM python:3.8

RUN mkdir /src
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /src/

RUN pip install -e .
EXPOSE 5000
CMD ["python", "/src/examples/resnet18_server.py"]
