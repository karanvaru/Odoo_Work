FROM alpine:3.10
ENV TZ=Europe/Moscow

RUN apk add --no-cache python3 py3-pip tini tzdata ipset iptables\
    tcpdump iftop ngrep bash vim screen curl openssl salt-minion \
    asterisk asterisk-curl asterisk-sounds-en asterisk-sounds-moh asterisk-srtp

ARG TARGETPLATFORM
RUN if [ "$TARGETPLATFORM" = "linux/amd64" ] ; then wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-alpine-linux-amd64-v0.6.1.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-v0.6.1.tar.gz \
    && rm dockerize-alpine-linux-amd64-v0.6.1.tar.gz ; fi

RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ] ; then wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-armhf-v0.6.1.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-armhf-v0.6.1.tar.gz \
    && rm dockerize-linux-armhf-v0.6.1.tar.gz ; fi

COPY ./etc/asterisk/ /etc/asterisk/


RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./docker-entrypoint.sh /
COPY ./bin/setup_queuelog.py /usr/local/bin/
COPY ./bin/setup_security.sh /usr/local/bin/
COPY ./bin/ast_tls_cert.sh /usr/local/bin/

RUN mkdir /srv/salt
COPY ./bin/sounds.sls /srv/salt/
RUN echo 'file_client: local' > /etc/salt/minion
RUN salt-call --local state.apply sounds

ENTRYPOINT ["/docker-entrypoint.sh"]
