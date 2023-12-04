FROM python:3.11
RUN pip install --upgrade pip
WORKDIR /code
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    cmake \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt /code/requirements.txt
RUN pip3 install -r requirements.txt
COPY ./app /code/app
HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health
ENTRYPOINT ["streamlit", "run", "app/Home.py", "--server.port=80", "--server.address=0.0.0.0"]