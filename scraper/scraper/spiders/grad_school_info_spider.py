import os
import scrapy
from urllib.parse import urlparse
import re
import json
from markdownify import markdownify as md

class GradSchoolInfoSpider(scrapy.Spider):
    name = 'grad_school_info_spider'
    allowed_domains = [
        'grad.rutgers.edu',
        'grad.admissions.rutgers.edu',
        'gradstudy.rutgers.edu'
    ]
    start_urls = [
        'https://grad.rutgers.edu/',
        'https://grad.admissions.rutgers.edu/',
        'https://gradstudy.rutgers.edu/'
    ]
    visited_urls = set()

    def parse(self, response):
        current_url = self.normalize_url(response.url)
        if current_url in self.visited_urls:
            return
        self.visited_urls.add(current_url)

        for href in response.css('a::attr(href)').getall():
            url = self.normalize_url(response.urljoin(href))
            if url not in self.visited_urls and urlparse(url).netloc in self.allowed_domains:
                yield scrapy.Request(url, callback=self.parse_page_content)

        yield from self.parse_page_content(response)

    def normalize_url(self, url):
        parsed_url = urlparse(url)
        normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        return normalized_url.rstrip('/')

    def parse_page_content(self, response):
        title = response.css('title::text').get() or 'No title'
        body_html = response.css('body').get() or 'No content'
        body_markdown = md(body_html)

        markdown_content = f"# {title}\n\n{body_markdown}\n\n---\n\n"

        domain = urlparse(response.url).netloc
        filename_base = self.sanitize_filename(title)
        markdown_filename = filename_base + '.md'
        html_filename = filename_base + '.html'
        
        folder_path = os.path.join('..', 'data', self.name, domain)

        os.makedirs(folder_path, exist_ok=True)

        self.write_content(folder_path, html_filename, body_html)
        markdown_file_path = self.write_content(folder_path, markdown_filename, markdown_content)
        self.update_metadata(folder_path, markdown_file_path, title, response.url)

        self.log(f'Saved files {markdown_filename} and {html_filename} in {folder_path}')

    def sanitize_filename(self, title):
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', title)
        filename = re.sub(r'[ .]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)
        return '_'.join(filename.split('_')[:10])

    def write_content(self, folder_path, filename, content):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return file_path

    def update_metadata(self, folder_path, md_filepath, title, url):
        metadata_file_path = os.path.join(folder_path, 'metadata.json')
        if os.path.exists(metadata_file_path):
            with open(metadata_file_path, 'r', encoding='utf-8') as file:
                metadata = json.load(file)
        else:
            metadata = {}

        relative_path = os.path.relpath(md_filepath, start=os.path.join('..', 'data'))
        metadata[relative_path] = {'title': title, 'url': url}

        with open(metadata_file_path, 'w', encoding='utf-8') as file:
            json.dump(metadata, file, indent=4)
