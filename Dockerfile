FROM python
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
RUN playwright install-deps && \
    playwright install
COPY . /app
WORKDIR /app/pragetx_scraper
RUN scrapy crawl pages && \
    cd /app && \
    python setup.py
WORKDIR /app
EXPOSE 7860
CMD ["python", "main.py"]
