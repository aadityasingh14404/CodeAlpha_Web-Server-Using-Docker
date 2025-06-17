#Choose base image
FROM python:3.9.22-alpine3.21

#work directory
WORKDIR /app

#install requirements
COPY requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt

#remove requiments file
RUN rm requirments.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]