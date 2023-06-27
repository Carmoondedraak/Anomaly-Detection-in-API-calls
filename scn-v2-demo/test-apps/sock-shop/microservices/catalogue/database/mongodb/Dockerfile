FROM alpine:3.9

LABEL maintainer="John MALAK."

COPY docker-entrypoint.sh /usr/local/bin/

RUN set -x \
    && addgroup -S mongodb \
    && adduser -Sg mongodb mongodb \
    && echo "@edge http://dl-cdn.alpinelinux.org/alpine/edge/main" \
        >> /etc/apk/repositories \
    && apk update \
    && apk add -u --no-cache \
        bash \
        jq \
        mongodb \
        numactl@edge \
        su-exec \
    && rm -rf /var/lib/mongodb \
    && mkdir -p /docker-entrypoint-initdb.d /data/db /data/configdb \
    && chown -R mongodb:mongodb /data/db /data/configdb \
    && ln -s usr/local/bin/docker-entrypoint.sh / # backward compatibility

VOLUME /data/db /data/configdb

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 27017
CMD ["mongod"]