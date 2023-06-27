FROM alpine:3.9

LABEL maintainer="John MALAK."

COPY docker-entrypoint.sh /usr/local/bin/

ENV PATH="/usr/local/bin/:${PATH}"

RUN set -x \
    && addgroup -S mongo \
    && adduser -Sg mongo mongo \
    && echo "@edge http://dl-cdn.alpinelinux.org/alpine/edge/main" \
        >> /etc/apk/repositories \
    && apk update \
    && apk add -u --no-cache \
        bash \
        jq \
        mongo \
        numactl@edge \
        su-exec \
    && rm -rf /var/lib/mongo \
    && mkdir -p /docker-entrypoint-initdb.d /data/db /data/configdb \
    && chown -R mongo:mongo /data/db /data/configdb \
    && ln -s usr/local/bin/docker-entrypoint.sh / # backward compatibility

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

VOLUME /data/db /data/configdb

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 27017
CMD ["mongod"]