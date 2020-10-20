FROM python:3.7-slim

# default env variables
ENV PORT=5000
ENV N_WORKERS=4


# set workdir
WORKDIR /app

# copy and install requirements
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# copy app code
COPY app.py /app
COPY neurogui /app/neurogui
COPY static /app/static
COPY templates /app/templates

# run app
CMD gunicorn app:app --workers=$N_WORKERS --bind=0.0.0.0:$PORT
