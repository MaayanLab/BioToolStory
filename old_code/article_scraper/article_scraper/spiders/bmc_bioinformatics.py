import scrapy, os, json, re
from inline_requests import inline_requests
import time
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.firefox.options import Options
import pycountry

# Check URL
check_url = lambda x: not any(['supplementary' in x.css('::text').extract_first().lower() if x.css('::text').extract_first() else False, '@' in x.css('::text').extract_first(), x.css('::attr("href")').extract_first() == None])

class JournalSpider(scrapy.Spider):

    # Setup
    name = "bmc_bioinformatics"
    start_urls = ['https://bmcbioinformatics.biomedcentral.com/articles']

    # Parse archive
    def parse(self, response):

        # Get minimum page
        from_page = 1

        # Loop through pages
        for page in list(range(1, 194)):

            # Parse year
            yield scrapy.Request('https://bmcbioinformatics.biomedcentral.com/articles?searchType=journalSearch&sort=PubDate&page='+str(page), callback=self.parse_page)

    # Parse page
    @inline_requests
    def parse_page(self, response):
        # Define articles
        articles = {'article_data': []}

        # Get page
        page = response.url.split('=')[-1]
        print("page:"+str(page))

        # Get base directory
        basedir = os.path.join(os.path.dirname(os.getcwd()), 's1-spider_results.dir/bmc_bioinformatics/')
        file = 'bmc-bioinformatics_page_'+str(page)+'.json'
        outfile = os.path.join(basedir, file)
  
        # Check if outfile exists
        if not os.path.exists(outfile):
     
            # Get articles
            article_links = ['https://bmcbioinformatics.biomedcentral.com'+x for x in response.css('ol[data-test="results-list"] li [data-test="title-link"]::attr(href)').extract()]

            # Loop through articles
            for i, article_link in enumerate(article_links):
            
                # Parse archive
                article = yield scrapy.Request(article_link)

                # # Get affiliation for last author, extract country and institution using selenium 
                # options = Options()
                # options.add_argument("--headless")
                # driver = webdriver.Firefox(options = options)
                # driver.get(article_link)
                # buttons = driver.find_elements_by_xpath("//li[@data-jumpto='Aff']")[-1] # click on last author for info
                # buttons.click()
                # html = driver.page_source
                # soup = BeautifulSoup(html, 'html.parser')
                # driver.close()

                #  #  Get all last author affiliations, countries, and institutions
                # last_author_all_affiliations = 'NaN'
                # country = 'NaN'
                # institutions = 'NaN'

                # try:
                #     last_author_all_affiliations = soup.find_all('li', {"class": "tooltip-tether__indexed-item"})    #.get_text(strip=True) # get the first affiliation for the last author 
                #     last_author_all_affiliations =[x.get_text(strip=True) for x in last_author_all_affiliations]
                    

                    # def GetCountry(segments):
                    #     final = []
                    #     for seg in segments:
                    #         seg = re.sub(r'\w*\d\w*\s', '', seg).strip() # remove words containing numbers like zip codes 
                    #         seg = re.sub(r'\sand$', '', seg).strip() # remove the word 'and' at the end of a string
                    #         seg = re.compile('[\W_]+').sub(' ', seg) # remove non word characters
                    #         seg = re.compile('^[the\s]+',re.IGNORECASE).sub('', seg) # remove 'the' at the beginning of a string
                    #         seg = seg.strip()
                    #         if seg == 'UK':
                    #             final.append('United Kingdom')
                    #         else:
                    #             if 'china' in seg.lower():
                    #                 final.append('China')
                    #             else:
                    #                 try:
                    #                     final.append(pycountry.countries.get(alpha_3=seg).name)
                    #                 except:
                    #                     try:
                    #                         final.append(pycountry.countries.get(name=seg).name)
                    #                     except:
                    #                         try:
                    #                             final.append(pycountry.countries.get(official_name=seg).name)
                    #                         except:
                    #                             try:
                    #                                 final.append(pycountry.countries.get(common_name=seg).name)
                    #                             except:
                    #                                 pass
                        
                    #     return(final)
                    
                    # all_segments = []
                    # for x in last_author_all_affiliations:
                    #     x = x.split(',')
                    #     for seg in x:
                    #         all_segments.append(seg.strip())

                    # country = GetCountry(all_segments)
                    
                    
                    # # extract institution from each affiliation using major keywords
                    # keywords = ['universi','instit','center','centre','academy','college','school']
                    # #single_affiliations = re.split(r';\d;', last_author_all_affiliations) # split each affiliation and find institution 
                    # institutions = []
                    # for aff in last_author_all_affiliations:
                    #     institution = 'NaN'
                    #     for keyword in keywords:
                    #         if len(re.findall(keyword, aff.lower()))>0:
                    #             institution = [x for x in aff.split(',') if keyword in x.lower()]
                    #             institution = [x.strip() for x in institution][0]
                    #             institution =  re.sub('\sand$', '', institution).strip()
                    #             institutions.append(institution)
                    #             break
                    # if len(institutions)== 0:
                    #     for aff in last_author_all_affiliations:
                    #         institution = str(aff.split(',')[1]).strip()
                    #         institution = re.sub('\sand$', '', institution).strip()
                    #         institutions.append(institution)
                    
                    
                    
                    # # extract institution from each affiliation using major keywords
                    # keywords = ['universi','college','school', 'instit','center','academy']
                    # #single_affiliations = re.split(r';\d;', last_author_all_affiliations) # split each affiliation and find institution 
                    # institutions = []
                    # for affiliation in last_author_all_affiliations:
                    #     affiliation = affiliation.split(',')
                    #     for aff in affiliation:
                    #         aff = aff.strip()
                    #         for keyword in keywords:
                    #             institution = 'NaN'
                    #             if len(re.findall(keyword, aff.lower()))>0:
                    #                 institution = [x for x in aff.split(';') if keyword in x.lower()]
                    #                 institution = [x.strip() for x in institution][0]
                    #                 institution =  re.sub('\sand$', '', institution).strip()
                    #                 institutions.append(institution)
                    #                 break
                    #             if institution != 'NaN':
                    #                 break
                    # if len(institutions)== 0:
                    #     for aff in ast_author_all_affiliations:
                    #         institution = str(aff.split(',')[1]).strip()
                    #         institution = re.sub('\sand$', '', institution).strip()
                    #         institutions.append(institution)
                    
                # except:
                #     pass



                    # Get country at the end of the affiliation
                    #country = affiliation.split(', ')[-1]
            
                    # # Get Institution
                    # # Extract the first institution found 
                    # # Loop through major keywords and find the first hit
                    # # If no hits, take the second term after splitting by colon which is usually an institution name 
                    # institution='NaN'
                    # keywords = ['universi','college','school', 'instit','center','academy']
                    # for keyword in keywords:
                    #     for aff in affiliation.split(', ')[1:]:
                    #         if len(re.findall(keyword, aff.lower()))>0:
                    #             #institution = re.sub("[^a-zA-Z\s-]+", "", aff).strip()
                    #             institution =  re.sub('\sand$', '', institution).strip()
                    #             break
                    #     if institution != 'NaN':
                    #         break
                    # if institution == 'NaN':
                    #     institution = str(affiliation.split(', ')[1]).strip()
                    #     institution = re.sub('\sand$', '', institution).strip()
                    #     #institution = re.sub("[^a-zA-Z\s-]+", "", institution).strip()
                # print('**********************************************')
                # print(last_author_all_affiliations)
                # print(country)
                # print(institutions)
                # print('**********************************************')
                # except:
                #     pass
                # Get data
                articles['article_data'].append({
                    'article_title': ''.join(article.css('.ArticleTitle::text, .ArticleTitle em::text').extract()),
                    'authors': [x.replace(u'\u00a0', ' ') for x in article.css('.u-listReset .AuthorName::text').extract()],
                    # 'last_author_affiliation': last_author_all_affiliations,
                    'doi': article.css('.ArticleDOI a::text').extract_first(),
                    'abstract': [[div.css('.Heading::text').extract_first().strip(), ''.join(div.css('.Para::text, .Para span::text').extract()).strip()] for div in article.css('.Abstract .AbstractSection')],
                    'date': article.css('[itemprop="datePublished"]::text').extract_first().replace(u'\u00a0', ' '),
                    'links': list(set([a.css('::attr("href")').extract_first() for a in article.css('.Abstract .AbstractSection a') if a.css('::text').extract_first() if check_url(a)]))
                })

            # Save data
            with open(outfile, 'w') as openfile:
                    openfile.write(json.dumps(articles, indent=4))


