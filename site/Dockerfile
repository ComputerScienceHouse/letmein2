FROM python:3.9.8-bullseye
LABEL maintainer="Joseph Abbate <josephabbateny@gmail.com>"

WORKDIR /app/
COPY ./requirements.txt /app/
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app/

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8080"]
