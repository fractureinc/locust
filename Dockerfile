
FROM python:3.7-alpine

COPY requirements.txt requirements.txt
RUN apk --no-cache add --virtual=.build-dep \
      build-base \
    && apk --no-cache add bash g++ zeromq-dev libffi-dev python3-dev openssl-dev \
    && pip install -r requirements.txt \
    && apk del .build-dep

# COPY licenses, sample tasks and entrypoint into root
COPY app /usr/src/app/
# Set script to be executable
RUN chmod 755 /usr/src/app/entrypoint.sh \
&& adduser appuser --uid 1001 --system --disabled-password \
&& chown -R appuser /usr/src/app && chmod u+x /usr/src/app/entrypoint.sh
USER appuser 
# Expose the required Locust ports
EXPOSE 5557 5558
# Start Locust using LOCUS_OPTS environment variable
ENTRYPOINT ["/usr/src/app/entrypoint.sh"] 