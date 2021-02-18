FROM python:3.7-alpine
COPY requirements.txt requirements.txt
RUN apk --no-cache add --virtual=.build-dep \
      build-base gcc musl-dev cargo\
    && apk --no-cache add bash g++ zeromq-dev libffi-dev python3-dev openssl-dev \
    && pip install --upgrade pip && pip install -r requirements.txt \
    && apk del .build-dep
COPY app /usr/src/app/
RUN chmod 755 /usr/src/app/entrypoint.sh \
    && adduser appuser --uid 1001 --system --disabled-password \
    && chown -R appuser /usr/src/app && chmod u+x /usr/src/app/entrypoint.sh
USER appuser 
EXPOSE 5557 5558
ENTRYPOINT ["/usr/src/app/entrypoint.sh"] 