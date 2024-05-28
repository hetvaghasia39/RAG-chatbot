import scrapy
import os
from markdownify import MarkdownConverter

class ImageBlockConverter(MarkdownConverter):
    """
    Create a custom MarkdownConverter that adds two newlines after an image
    """
    def convert_img(self, el, text, convert_as_inline):
        # print("el", el)
        # print("text", text)
        # print("conve", convert_as_inline)
        alt_text = el.get('alt')
        # print("alt text:", alt_text)
        return f"IMAGE: {alt_text}\n"

# Create shorthand method for conversion
def md(html, **options):
    return ImageBlockConverter(**options).convert(html)

class PagesSpider(scrapy.Spider):
    name = "pages"
    allowed_domains = ["pragetx.com"]
    start_urls = ["https://pragetx.com"]

    def start_requests(self):
        url = "https://pragetx.com"
        print("Starting request")
        print("URL", url)
        yield scrapy.Request(url, meta={'playwright': True})

    def parse(self, response):
        if not os.path.exists("data"):
            os.makedirs("data")
        with open(f"data/{response.url.strip('/').split('//')[-1].replace('/', '.')}.md", "w") as f:
            file_content = f"""# {response.url}\n\n"""
            file_content += md(response.text)
            f.write(file_content)
        yield {
            "url": response.url,
            "title": response.css("title::text").get(),
            "body": md(response.text),
        }
        for link in response.css("a::attr(href)").getall():
            try:
                yield response.follow(response.urljoin(link), callback=self.parse)
            except:
                pass
        
