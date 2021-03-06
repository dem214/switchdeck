FROM minio/minio

RUN apt-get install wget dpkg

RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc
RUN chmod +x mc
RUN mc alias set myminio/ http://MINIO-SERVER MYUSER MYPASSWORD

RUN mc admin user add ${MINIO_ALIAS} ${MINIO_ACCESSKEY} ${MINIO_SECRETKEY}
RUN mkdir /data

ENTRYPOINT [ "server" "/data" ]

