FROM alpine:latest
WORKDIR /app
COPY *.py MumbleServer.ice requirements.txt /app/
RUN apk add python3 olm py3-pip
RUN apk add g++ make python3-dev openssl-dev bzip2-dev  # needed for zeroc-ice build
RUN python3 -m venv .venv
RUN <<EOF
    . .venv/bin/activate
    pip3 install -r requirements.txt
    slice2py MumbleServer.ice
EOF
ENTRYPOINT [".venv/bin/python3", "main.py"]
