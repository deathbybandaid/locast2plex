FROM jrottenberg/ffmpeg:4.0-alpine
LABEL maintainer="Thomas Gorgolione <thomas@tgorg.com>"

RUN apk add --no-cache --update python3
RUN pip3 install -r requirements.txt
COPY data /app/data
COPY *.py /app/

ENTRYPOINT ["python3", "/app/main.py", "2>&1"]
