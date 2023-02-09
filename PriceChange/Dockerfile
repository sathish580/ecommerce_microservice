FROM python:3.9
WORKDIR /usr/src/app
COPY ./PriceChange/requirements.txt ./PriceChange/invokes.py ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./PriceChange/price_change.py .
CMD [ "python", "./price_change.py" ]