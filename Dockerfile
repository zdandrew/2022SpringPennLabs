FROM python:3.8-slim
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install -r requirements.txt
ADD . .
ENTRYPOINT ["./start_app_w_gunicorn.sh"]
