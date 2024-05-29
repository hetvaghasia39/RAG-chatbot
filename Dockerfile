FROM python
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app
RUN playwright install-deps && \
    playwright install

COPY --chown=user . $HOME/app
WORKDIR $HOME/app/pragetx_scraper
RUN scrapy crawl pages && \
    cd $HOME/app && \
    python setup.py
WORKDIR $HOME/app
EXPOSE 7860
CMD ["python", "main.py"]
