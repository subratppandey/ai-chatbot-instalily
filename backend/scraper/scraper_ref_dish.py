import scrapy
import openai
import os
import re
from pinecone import Pinecone, ServerlessSpec
from scrapy.crawler import CrawlerProcess
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_HOST_URL = os.getenv("PINECONE_HOST_URL")
PINECONE_INDEX = '143'

class DishwasherRefrigeratorSpider(scrapy.Spider):
    name = "dishwasher_refrigerator"
    allowed_domains = ["partselect.com"]
    start_urls = [
        "https://www.partselect.com/Dishwasher-Models.htm",
        "https://www.partselect.com/Refrigerator-Models.htm",
        ]

    def __init__(self, *args, **kwargs):
        super(DishwasherRefrigeratorSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

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
                    region='us-east-1' 
               )
           )

        # Access the Pinecone index
        self.index = self.pc.Index(PINECONE_INDEX)

        # Initialize OpenAI API
        openai.api_key = OPENAI_API_KEY

    def parse(self, response):
        # Follow links to model pages
        model_links = response.css("ul.nf__links a::attr(href)").getall()
        for link in model_links:
            absolute_url = response.urljoin(link)
            yield scrapy.Request(absolute_url, callback=self.parse_model)

        # Follow pagination if present
        next_page = response.css("ul.pagination li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_model(self, response):
        """Scrape a single model page and its parts."""
        model_id = response.url.split("/")[-2]
        model_name = response.css('h1.title-main::text').get().split("-")[0].strip()
        appliance_type = 'Dishwasher' if re.search(r'Dishwasher', response.url, re.IGNORECASE) \
            else 'Refrigerator' if re.search(r'Refrigerator', response.url, re.IGNORECASE) \
            else "Unknown"

        # Extract parts for the model
        parts_links = response.css("a.mega-m__part__name::attr(href)").getall()
        for part_link in parts_links:
            absolute_url = response.urljoin(part_link)
            yield scrapy.Request(absolute_url, callback=self.parse_part, meta={'model_id': model_id, 'model_name': model_name, 'appliance_type': appliance_type})

    def parse_part(self, response):
        """Scrape a single part and its details."""
        part_id = response.css('span[itemprop="productID"]::text').get()
        part_name = response.css('span[itemprop="name"]::text').get().strip()
        part_price = response.css('span[itemprop="price"] span.js-partPrice::text').get()
        if part_price is None:
            part_price = "N/A"
        part_info = response.css('div[itemprop="description"]::text').get()

        video = response.xpath("//div[@id='PartVideos']/following-sibling::div[1]//div/@data-yt-init").get()

        # Use 'or' to assign the YouTube link if youtube_id exists, otherwise None
        video_link = f"https://www.youtube.com/watch?v={video}" if video else None

        # Additional troubleshooting information
        fixes = response.xpath('//div[@id="Troubleshooting"]/following-sibling::div[1]/div[1]/text()').get(default='').strip()
        compatibility = response.xpath('//div[@id="Troubleshooting"]/following-sibling::div[1]/div[2]/text()').get(default='').strip()

        # Aggregate text for embedding
        scraped_text = f"{part_id} - {part_name} - {part_info}. Price: {part_price}. Fixes: {fixes}. Compatibility: {compatibility}. Video: {video_link}"

        # Generate embeddings using OpenAI's embedding model
        embedding = self.get_openai_embedding(scraped_text)

        # Store embeddings and metadata in Pinecone
        metadata = {
            'model_id': response.meta['model_id'],
            'model_name': response.meta['model_name'],
            'appliance_type': response.meta['appliance_type'],
            'part_id': part_id,
            'part_name': part_name,
            'part_price': part_price,
            'url': response.url,
        }

       # Only add video_link if it's not None because Metadata can't be of null type
        if video_link:
            metadata['video_link'] = video_link

        response = self.index.upsert([(part_id, embedding, metadata)])
        print(f"Pinecone Upsert Response: {response}")

    def get_openai_embedding(self, text):
        """Generate embeddings using OpenAI's text-embedding-ada-002 model."""
        try:
            response = openai.embeddings.create(input=[text], model="text-embedding-ada-002")
            embedding = response.data[0].embedding
            print(f"Embedding generated successfully for text: {text[:10]}...")  # Log for successful embedding
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}") 
            return None  # Return None to indicate failure

# Function to run the spider
def run_spider():
    process = CrawlerProcess(settings={
        'DEPTH_LIMIT': 8,
        'LOG_LEVEL': 'INFO'
    })
    process.crawl(DishwasherRefrigeratorSpider)
    process.start()

if __name__ == "__main__":
   run_spider()
