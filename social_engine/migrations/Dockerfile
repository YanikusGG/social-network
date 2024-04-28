FROM liquibase/liquibase:4.19.0

WORKDIR /app

COPY . /app

CMD ["liquibase", "update", "--defaults-file=liquibase.properties"]
