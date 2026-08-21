# ---- Backend image ----
# Light by default (TF-IDF semantic engine). To bake in transformer embeddings,
# build with:  docker build --build-arg INSTALL_ML=true -t resume-api ./backend
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install core dependencies first (better layer caching).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optionally add the heavyweight ML stack (sentence-transformers, spaCy).
ARG INSTALL_ML=false
COPY requirements-ml.txt .
RUN if [ "$INSTALL_ML" = "true" ]; then \
      pip install --no-cache-dir -r requirements-ml.txt && \
      python -m spacy download en_core_web_sm ; \
    fi

COPY app ./app

# Run as a non-root user.
RUN useradd -m appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
