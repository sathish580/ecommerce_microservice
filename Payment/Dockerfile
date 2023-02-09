FROM python:3.9
WORKDIR /usr/src/app
RUN mkdir templates   
COPY ./Payment/requirements.txt ./Payment/amqp_setup.py ./Payment/templates/index.html ./
RUN mv index.html templates
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./Payment/app.py .
CMD [ "python", "./app.py", "" ]
