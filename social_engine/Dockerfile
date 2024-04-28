FROM python:3.10

WORKDIR /app

COPY social_engine/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY social_engine /app

COPY proto /app/lib/proto
RUN bash /app/lib/proto/compile.sh

ENTRYPOINT ["python", "-m", "main"]
