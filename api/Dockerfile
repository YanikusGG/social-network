FROM python:3.10

WORKDIR /app

COPY api/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY api /app

COPY proto /app/lib/proto
RUN bash /app/lib/proto/compile.sh

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
