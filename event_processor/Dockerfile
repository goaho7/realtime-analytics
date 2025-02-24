FROM python:3.12

WORKDIR /event_processor

COPY . .


RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
RUN poetry install --no-root

CMD ["poetry", "run", "python", "main.py"]
