
FROM python:3.7-alpine

COPY requirements.txt requirements.txt
RUN apk --no-cache add --virtual=.build-dep \
      build-base \
    && apk --no-cache add curl jq bash g++ zeromq-dev libffi-dev python3-dev openssl-dev \
    && pip install -r requirements.txt \
    && apk del .build-dep

# COPY licenses, sample tasks and entrypoint into root
COPY app /
# Set script to be executable
RUN chmod 755 /entrypoint.sh /reporter.sh 
# Expose the required Locust ports
EXPOSE 5557 5558
# Start Locust using LOCUS_OPTS environment variable
ENTRYPOINT ["/entrypoint.sh"] 