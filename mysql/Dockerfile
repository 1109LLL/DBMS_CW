FROM mysql:8.0.23

ENV MYSQL_DATABASE movie_site
ENV MYSQL_ROOT_PASSWORD=password
ENV MYSQL_USER: "${DB_USERNAME}"
ENV MYSQL_PASSWORD: "${DB_PASSWORD}"

RUN mkdir generated_csv
COPY ./generated_csv/ /generated_csv/
RUN chmod -R 777 /generated_csv/

COPY ./conf/my.cnf /etc/mysql/conf.d/

COPY ./scripts/ /docker-entrypoint-initdb.d/
RUN chmod -R 777 docker-entrypoint-initdb.d
