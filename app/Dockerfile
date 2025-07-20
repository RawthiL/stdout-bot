FROM python:3.12-alpine


# create default working directory
WORKDIR /home/app/code

COPY requirements.txt /home/app/code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /home/app/code/requirements.txt


COPY src /home/app/code

CMD ["python", "main.py"]

