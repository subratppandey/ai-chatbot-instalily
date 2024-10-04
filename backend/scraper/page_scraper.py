import scrapy
import openai
import os
import re
from pinecone import Pinecone, ServerlessSpec
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags_with_content
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_HOST_URL = os.getenv("PINECONE_HOST_URL")
PINECONE_INDEX = '143'

class GeneralPagesSpider(scrapy.Spider):
    name = "general_pages"
    allowed_domains = ["partselect.com"]
    start_urls = ["https://www.partselect.com/"]

    def __init__(self, *args, **kwargs):
        super(GeneralPagesSpider, self).__init__(*args, **kwargs)
        self.seen_urls = set()

        # Initialize Pinecone client using the new Pinecone class
        self.pc = Pinecone(api_key=PINECONE_API_KEY, host_url=PINECONE_HOST_URL)

        # Check if the index exists, create it if not
        if PINECONE_INDEX not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=PINECONE_INDEX,
                dimension=1536, 
                metric='cosine', 
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east1' 
                )
            )

        # Access the Pinecone index
        self.index = self.pc.Index(PINECONE_INDEX)

        # Initialize OpenAI API
        openai.api_key = OPENAI_API_KEY

    def parse(self, response):
        # Keep track of visited URLs to avoid revisiting
        self.seen_urls.add(response.url)

        # Scrape general content from the page
        self.scrape_general_page(response)

       # Follow links recursively for general pages
        page_links = response.css("a::attr(href)").getall()
        for link in page_links:
            absolute_url = response.urljoin(link)
            # Ensure we only follow internal links and avoid revisiting
            if absolute_url.startswith('https://www.partselect.com/') and absolute_url not in self.seen_urls:
                yield scrapy.Request(absolute_url, callback=self.parse)

    def clean_body_text(self, response):
        """Clean the response body by removing unnecessary elements."""
        # Extract text while removing certain tags (e.g., script, style, etc.)
        clutters = ['script', 'style', 'footer', 'header', 'nav', 'img', 'aside', 'noscript']
      
        # Remove these elements using Scrapy's built-in remove_tags_with_content
        cleaned_html = response.text
        for tag in clutters:
            cleaned_html = remove_tags_with_content(cleaned_html, which_ones=tag)

        # Parse the cleaned HTML again with Scrapy's selector
        response_selector = scrapy.Selector(text=cleaned_html)

        # Extract the cleaned text from the remaining elements
        body_text = ' '.join(response_selector.xpath('//body//text()').getall()).strip()

        # Remove excessive whitespace and newlines
        body_text = re.sub(r'\s+', ' ', body_text).strip()
      
       return body_text

   def scrape_general_page(self, response):
       """Scrape general content from any page."""
        page_title = response.css('title::text').get().strip()
        body_text = self.clean_body_text(response)

        video = response.xpath("//div[@id='PartVideos']/following-sibling::div[1]//div/@data-yt-init").get()

        # Assign YouTube link if video exists, otherwise None
        video_link = f"https://www.youtube.com/watch?v={video}" if video else None

        # Generate embeddings for the general page content
        embedding = self.get_openai_embedding(body_text)

        # Store the embedding and metadata in Pinecone
        metadata = {
            'url': response.url,
            'page_title': page_title,
            }

        if video_link:
            metadata['video_link'] = video_link

        self.index.upsert([(response.url, embedding, metadata)])

   def get_openai_embedding(self, text):
       """Generate embeddings using OpenAI's text-embedding-ada-002 model."""
       try:
            response = openai.embeddings.create(input=[text], model="text-embedding-ada-002")
            embedding = response.data[0].embedding
            return embedding
       except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return None

# Function to run the spider
def run_spider():
    process = CrawlerProcess(settings={
        'DEPTH_LIMIT': 8,
        'LOG_LEVEL': 'INFO'
    })
    process.crawl(GeneralPagesSpider)
    process.start()

if __name__ == "__main__":
    run_spider()


