FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements-backend.txt ./
RUN pip install --no-cache-dir -r requirements-backend.txt
COPY src ./src
COPY web ./web
COPY build ./build
COPY evidence ./evidence
COPY data ./data
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/readyz',timeout=3)"
CMD ["gunicorn","--bind","0.0.0.0:8000","--workers","2","--worker-class","gthread","--threads","2","--timeout","45","--access-logfile","-","--error-logfile","-","src.wsgi:application"]
