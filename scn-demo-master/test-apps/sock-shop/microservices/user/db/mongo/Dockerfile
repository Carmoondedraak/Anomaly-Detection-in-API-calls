FROM mongo:4.2.0
ENV MONGO_INITDB_ROOT_USERNAME=admin-user
ENV MONGO_INITDB_ROOT_PASSWORD=admin-pass
ENV MONGO_INITDB_DATABASE=users
ENV dbUser=app-user
ENV dbPwd=app-pass
COPY ./run.sh /docker-entrypoint-initdb.d/