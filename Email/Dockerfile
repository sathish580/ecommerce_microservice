FROM python:3.9
WORKDIR /usr/src/app
COPY ./Email/requirements.txt ./Email/amqp_setup.py ./Email/invokes.py ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./Email/emailer.py .
CMD [ "python", "./emailer.py" ]