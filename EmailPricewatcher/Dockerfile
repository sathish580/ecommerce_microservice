FROM python:3.9
WORKDIR /usr/src/app
COPY ./EmailPricewatcher/requirements.txt ./EmailPricewatcher/amqp_setup.py ./EmailPricewatcher/invokes.py ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./EmailPricewatcher/email_pricewatchers.py .
CMD [ "python", "./email_pricewatchers.py" ]