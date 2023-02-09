FROM python:3-slim
WORKDIR /usr/src/app
COPY ./Image_To_Keyword/requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./Image_To_Keyword/image_to_keyword.py .
CMD [ "python", "./image_to_keyword.py" ]