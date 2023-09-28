FROM postgis/postgis:12-master
# FROM pgrouting/pgrouting:latest

RUN apt update && apt install -y postgresql-12-pgrouting

ENV POSTGRES_USER admin
ENV POSTGRES_PASSWORD 1234
ENV POSTGRES_DB pilot2

# 초기 DB 스키마 설치
# sql 파일이 여러개 있을 경우, alpha-numeric 순으로 처리됨.
COPY *.sql /docker-entrypoint-initdb.d/