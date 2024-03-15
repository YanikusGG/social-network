FROM liquibase/liquibase:4.19.0

WORKDIR /app

COPY . /app

CMD ["update", "--changelog-file=changelog.xml", "--url=jdbc:postgresql://api-postgresql:5432/api_service", "--username=api_service", "--password=api_service"]
