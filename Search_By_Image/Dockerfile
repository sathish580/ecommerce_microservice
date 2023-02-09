FROM python:3-slim
WORKDIR /usr/src/app
COPY ./Search_By_Image/requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./Search_By_Image/search_by_image.py .
CMD [ "python", "./search_by_image.py" ]