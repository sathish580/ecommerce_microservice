FROM python:3-slim
WORKDIR /usr/src/app
COPY ./Product/requirements.txt ./Product/leichachacha.json ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./Product/product.py .
CMD [ "python", "./product.py" ]