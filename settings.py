# settings.py

SPLASH_URL = 'http://192.168.29.74:8050'

DOWNLOADER_MIDDLEWARES = {
    'scrapyjs.SplashMiddleware': 725,
}

DUPEFILTER_CLASS = 'scrapyjs.SplashAwareDupeFilter'