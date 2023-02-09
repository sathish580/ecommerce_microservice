FROM python:3-slim
WORKDIR /usr/src/app
COPY ./Pricewatching/requirements.txt ./Pricewatching/leichachacha.json ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./Pricewatching/pricewatching.py .
CMD [ "python", "./pricewatching.py" ]