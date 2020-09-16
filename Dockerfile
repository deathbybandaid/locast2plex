FROM jrottenberg/ffmpeg:4.0-alpine
LABEL maintainer="Thomas Gorgolione <thomas@tgorg.com>"

RUN apk add --no-cache --update python3
COPY main.py /app/main.py
COPY data /app/data
COPY templates.py /app/templates.py
COPY SSDPServer.py /app/SSDPServer.py
COPY LocastService.py /app/LocastService.py
COPY m3u8/ /app/m3u8/

ENTRYPOINT ["python3", "/app/main.py", "2>&1"]
