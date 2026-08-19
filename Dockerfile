FROM python:3.11-slim
WORKDIR /app
COPY keepalive.py .
ENV MTA_IP=51.68.107.75
ENV MTA_PORT=12599
CMD python -u keepalive.py $MTA_IP $MTA_PORT -i 20
