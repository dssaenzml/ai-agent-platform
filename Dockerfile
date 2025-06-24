FROM python:3.11-slim

# Update and install required packages
RUN apt-get update && \
    apt-get install -y ffmpeg libsm6 libxext6 libmagic1 poppler-data poppler-utils && \
    apt-get install -y tesseract-ocr tesseract-ocr-ara tesseract-ocr-spa tesseract-ocr-por && \
    apt-get install -y libreoffice && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry version 2.1.1
RUN pip install poetry==2.1.1

# Configure Poetry to not create virtual environments
RUN poetry config virtualenvs.create false

# Set the working directory
WORKDIR /code

# Copy necessary files for Poetry
COPY ./pyproject.toml ./README.md ./poetry.lock* ./

# Copy the packages directory
COPY ./packages ./packages

# Install dependencies without creating a virtual environment
RUN poetry install --no-interaction --no-ansi --no-root --only main --verbose

# Copy the application code
COPY ./app ./app

# Copy the Python script and unstructured lib resources
COPY ./get_unstructured_lib_ready.py ./get_unstructured_lib_ready.py
COPY ./nltk_data_3.8.2.tar.gz ./nltk_data_3.8.2.tar.gz

# Install the application dependencies
RUN poetry install --no-interaction --no-ansi --only main --verbose

# Run the Python script to process the documents
RUN python3 get_unstructured_lib_ready.py

# Expose the application port
EXPOSE 8080

# Command to run the application
CMD exec uvicorn app.server:app --host 0.0.0.0 --port 8080 \
--root-path $ROOT_PATH