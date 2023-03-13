FROM python:3.9
ADD app.py .
RUN pip install Flask requests flask_mysqldb datetime
CMD ["python", "./app.py"]

