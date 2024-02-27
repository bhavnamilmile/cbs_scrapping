from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os


class BLMContentScraper:
    # headers =  ['Headline', 'Author', 'Date', 'URL']
    headers = ['id', 'date published', 'source', 'headline', 'author', 'description', 'directory', 'link']
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        # Initialize all selectors and formats as None
        self.headline_selector = None
        self.author_selector = None
        self.date_selector = None
        self.url_selector = None
        self.date_format = None
        self.output_date_format = None
        self.article_selector = None

        self.description_selector = None

        self.id = None
        self.source = None

        self.body = None


        # self.headers = ['Headline', 'Author', 'Date', 'URL']
        #id, date published, source, headline, author, description, directory, link

    def fetch_article_body(self, article):
        NotImplemented


    def check_selectors_filled(self):
        """Check if all selector and format attributes are filled."""
        attributes = [self.headline_selector, self.author_selector, self.date_selector, 
                      self.url_selector, self.date_format, self.output_date_format, self.article_selector,
                      self.id, self.source, self.description_selector, self.body]
        return all(attributes)  # Returns False if any attribute is None


    def fetch_single_article(self, article):
        headline = article.select_one(self.headline_selector).text.strip() if article.select_one(self.headline_selector) else 'HEADLINE_NOT_FOUND'
        author = article.select_one(self.author_selector).text.strip() if article.select_one(self.author_selector) else 'AUTHOR_NOT_FOUND'
        date_str = article.select_one(self.date_selector).text.strip() if article.select_one(self.date_selector) else 'DATE_NOT_FOUND'
        url = article.select_one(self.url_selector)['href'] if article.select_one(self.url_selector) else 'URL_NOT_FOUND'
        description = article.select_one(self.description_selector).text.strip() if article.select_one(self.description_selector) else 'DESC_NOT_FOUND'
        try:
            print(date_str)
            date_obj = datetime.strptime(date_str, self.date_format)
            date = date_obj.strftime(self.output_date_format)
        except ValueError:
            date = 'INVALID_DATE_FORMAT'
        #headers = ['id', 'date published', 'source', 'headline', 'author', 'description', 'directory', 'link']
        curr_row = [self.id, date, self.source, headline, author, description, '', url]
        return curr_row
    
    def fetch_articles(self):
        # Implement fetching and processing articles based on defined selectors
        articles = self.soup.select(self.article_selector)
        data = []
        for article in articles:
            curr_row = self.fetch_single_article(article)
            data.append(curr_row) #[headline, author, date, url])
        return data

    @staticmethod
    def save_to_csv(data, csv_out):
        with open(csv_out, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            #Name	Location	Sources	Keywords	Author Name	Article Date	Source Link

            writer.writerow(BLMContentScraper.headers) #['Headline', 'Author', 'Date', 'URL'])
            for row in data:
                writer.writerow(row)
        print(f'Data written to {csv_out}')


class WSJScraper(BLMContentScraper):
    def __init__(self, id, html_content):
        super().__init__(html_content)
        self.headline_selector = 'div.WSJTheme--headline--7VCzo7Ay'
        self.author_selector = 'p.WSJTheme--byline--1oIUvtQ3'
        self.date_selector = 'time.WSJTheme--timestamp--22sfkNDv'
        self.url_selector = 'a'
        self.date_format = '%B %d, %Y %I:%M %p ET'
        self.output_date_format = '%m-%d-%Y'
        self.article_selector = 'article.WSJTheme--story--XB4V2mLz'
        self.description_selector = 'p.WSJTheme--summary--lmOXEsbN'
        self.body = 'p.body'

        self.id = id
        self.source = "WSJ"  # Make sure to set it correctly and use proper folder name convention
        # Check if all elements are filled
        if not self.check_selectors_filled():
            raise ValueError("One or more selectors or formats are not set.")

        # print("All OK")




class NBCScraper(BLMContentScraper):
    def __init__(self, id, html_content):
        super().__init__(html_content)
        self.headline_selector = 'h1.article-hero-headline__htag'
        self.author_selector = 'p.endmark'
        self.date_selector = 'time.relative'
        self.url_selector = 'a'
        self.date_format = '%B %d, %Y %I:%M %p ET'
        self.output_date_format = '%m-%d-%Y'
        self.article_selector = 'article.WSJTheme--story--XB4V2mLz'
        self.description_selector = 'div.styles_articleDek__Icz5H'

        self.body = 'div.article-body__content'

        self.id = id
        self.source = "NBCNews"  # Make sure to set it correctly and use proper folder name convention
        # Check if all elements are filled
        if not self.check_selectors_filled():
            raise ValueError("One or more selectors or formats are not set.")

    def fetch_article_body(self, article):

        article_paras = article.select(self.body)


        paragraph_selector = "p"

        paragraphs = article_paras[0].select(paragraph_selector)

        body_str = ""
        for para in paragraphs:
            body_str += para.text +"\n"
        return body_str

    def fetch_single_article(self, article, url):
        data = super().fetch_single_article(article)
        date_str = article.select_one(self.date_selector).attrs['datetime'] if article.select_one(self.date_selector) else 'DATE_NOT_FOUND'

        try:
            # Parse the datetime string
            date_time_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')

            date_str = date_time_obj.strftime(self.output_date_format)
        except ValueError:
            date_str = 'INVALID_DATE_FORMAT'

        data[1] = date_str
        data[-1] = url
        return data
    


class CBSScraper(BLMContentScraper):
    def __init__(self, id, html_content):
        super().__init__(html_content)
        self.headline_selector = 'h1.content__title '
        self.author_selector = 'span.byline__authors'
        self.date_selector = 'time.datetime'
        self.url_selector = 'a'
        self.date_format = '%B %d, %Y %I:%M %p ET'
        self.output_date_format = '%m-%d-%Y'
        self.article_selector = 'article.WSJTheme--story--XB4V2mLz'
        self.description_selector = 'div.styles_articleDek__Icz5H'

        self.body = 'section.content__body'

        self.id = id
        self.source = "CBSNews"  # Make sure to set it correctly and use proper folder name convention
        # Check if all elements are filled
        if not self.check_selectors_filled():
            raise ValueError("One or more selectors or formats are not set.")

    def fetch_article_body(self, article):

        article_paras = article.select(self.body)


        paragraph_selector = "p"

        paragraphs = article_paras[0].select(paragraph_selector)

        body_str = ""
        for para in paragraphs:
            body_str += para.text +"\n"
        return body_str

    def fetch_single_article(self, article, url):
        data = super().fetch_single_article(article)
        date_str = article.select_one(self.date_selector).attrs['datetime'] if article.select_one(self.date_selector) else 'DATE_NOT_FOUND'

        try:
            # Parse the datetime string
            date_time_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')

            date_str = date_time_obj.strftime(self.output_date_format)
        except ValueError:
            date_str = 'INVALID_DATE_FORMAT'

        data[1] = date_str
        data[-1] = url
        return data


    
def scrape_and_save(id, file_name, csv_out):
    with open(file_name) as f:
        html_content = f.read()
    scraper = WSJScraper(id, html_content)
    article_data = scraper.fetch_articles()
    
    # WSJScraper.save_to_csv(article_data, csv_out)
    return article_data

if __name__ == "__main__":
    id = "Michael Brown"
    source = "WSJ"
    
    source_path = os.path.join(id, source) # Assuming your HTML files are in a directory named "data"
    output_directory = os.path.join("results", source_path) 
    os.makedirs(output_directory, exist_ok=True)
    

    data_all = []
    # for WSJ
    print(source_path   )
    for keyword in os.listdir(source_path):
        full_kw_path = os.path.join(source_path, keyword)
        for curr_file in os.listdir(full_kw_path):
            print(curr_file)
            if curr_file.endswith(".txt"):  # Assuming the files are HTML files
                file_path = os.path.join(full_kw_path, curr_file)
                output_file_name = curr_file.split(".")[0] + ".csv"
                csv_out_path = os.path.join(output_directory, output_file_name)

                data = scrape_and_save(id, file_path, csv_out_path)
                data_all.extend(data)
    
    BLMContentScraper.save_to_csv(data_all, os.path.join(output_directory, keyword+".csv"))


        