FROM python:3.12

WORKDIR /user_api

COPY . .

# RUN pip install --upgrade pip
# RUN pip install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
RUN poetry install --no-root

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
