import scrapy, os, json, re
from inline_requests import inline_requests
import pycountry

# Check URL
check_url = lambda x: not any(['supplementary' in x.css('::text').extract_first().lower(), '@' in x.css('::text').extract_first(), x.css('::attr("href")').extract_first() == None])

class JournalSpider(scrapy.Spider):

    # Setup
    name = "oxford"
    journals = ['bioinformatics', 'nar', 'database']
    start_urls = ['https://academic.oup.com/'+x+'/issue-archive' for x in journals]

    # Parse archive
    def parse(self, response):

        # Get minimum year
        from_year = 2008

        # Loop through years
        for year_link in response.css('.widget-instance-OUP_Issues_Year_List div a::attr(href)').extract():

            # Minimum year
            if int(year_link.split('/')[-1]) >= from_year:
                
                # Parse year
                yield scrapy.Request('https://academic.oup.com'+year_link, callback=self.parse_year)

    # Parse year
    def parse_year(self, response):

        # Loop through archives
        for i, issue_link in enumerate(response.css('.widget-instance-OUP_Issues_List div a::attr(href)').extract()):

                
            # Parse archive
            yield scrapy.Request('https://academic.oup.com'+issue_link, callback=self.parse_issue)

    # Parse issue
    @inline_requests
    def parse_issue(self, response):

        # Define articles
        articles = {'article_data': []}

        # Split URL
        split_url = response.url.split('/')

        # Get journal name
        journal_name = split_url[3]

        # Get base directory
        basedir = os.path.join(os.path.dirname(os.getcwd()), 's1-spider_results.dir')

        # If database
        if journal_name == 'database':
            outfile = os.path.join(basedir, journal_name, '_'.join([journal_name, 'vol'+split_url[-1]])+'.json')
        else:
            outfile = os.path.join(basedir, journal_name, '_'.join([journal_name, 'vol'+split_url[-2], 'issue'+split_url[-1]])+'.json')

        # Check if outfile exists
        if not os.path.exists(outfile):

            # Loop through articles
            for i, article_link in enumerate(response.css('.viewArticleLink::attr(href)').extract()):


                # Parse archive
                article = yield scrapy.Request('https://academic.oup.com'+article_link)

                ## Get data ()
                article_title = ''.join(article.css('.wi-article-title::text, .wi-article-title em::text').extract()).strip()
                
                # Get list of all authors
                authors = article.css('.wi-authors .info-card-name::text').extract()

                #  Get all last author affiliations, countries, and institutions
                last_author_all_affiliations = 'NaN'
                # country = 'NaN'
                # institutions = 'NaN'

                try:
                        
                    #last_author_affiliation = ''.join(article.css('.info-card-affilitation::text, .info-card-affilitation sup::text')[-1].extract()).strip('\n\r').strip().rstrip(',').rstrip('.').replace(',',';')                
                    #last_author_all_affiliations = str([[';'.join(p.css('::text, sup::text').extract()).strip()] for p in article.css('.info-card-affilitation')][-1]).strip()
                    last_author_all_affiliations = [[';'.join(p.css('::text, sup::text').extract()).strip()] for p in article.css('.info-card-affilitation')][-1][0]
                    last_author_all_affiliations =last_author_all_affiliations.rstrip(',')
                    last_author_all_affiliations =last_author_all_affiliations.rstrip('.')
                    last_author_all_affiliations = last_author_all_affiliations.replace(',',';').strip()
                    last_author_all_affiliations= re.split(r';\d;', last_author_all_affiliations)
                    last_author_all_affiliations = [x.strip() for x in last_author_all_affiliations if x != '']
                    last_author_all_affiliations = [x.replace(';',',') for x in last_author_all_affiliations]
                    last_author_all_affiliations= [x.rstrip(',') for x in last_author_all_affiliations]
          

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
                except:
                    pass

                #     def GetCountry(segments):
                #         final = []
                #         for seg in segments:
                #             seg = re.sub(r'\w*\d\w*\s', '', seg).strip() # remove words containing numbers like zip codes 
                #             seg = re.sub(r'\sand$', '', seg).strip() # remove the word 'and' at the end of a string
                #             seg = re.compile('[\W_]+').sub(' ', seg) # remove non word characters
                #             seg = re.compile('^[the\s]+',re.IGNORECASE).sub('', seg) # remove 'the' at the beginning of a string
                #             seg = seg.strip()
                #             if seg == 'UK':
                #                 final.append('United Kingdom')
                #             else:
                #                 if 'china' in seg.lower():
                #                     final.append('China')
                #                 else:
                #                     try:
                #                         final.append(pycountry.countries.get(alpha_3=seg).name)
                #                     except:
                #                         try:
                #                             final.append(pycountry.countries.get(name=seg).name)
                #                         except:
                #                             try:
                #                                 final.append(pycountry.countries.get(official_name=seg).name)
                #                             except:
                #                                 try:
                #                                     final.append(pycountry.countries.get(common_name=seg).name)
                #                                 except:
                #                                     pass
                #         return(final)
                    
                #     country = GetCountry([x.strip() for x in last_author_all_affiliations.split(';')])
                    
                #     # extract institution from each affiliation using major keywords
                #     keywords = ['universi','college','school', 'instit','center','academy']
                #     single_affiliations = re.split(r';\d;', last_author_all_affiliations) # split each affiliation and find institution 
                #     institutions = []
                #     for aff in single_affiliations:
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
                #     if len(institutions)== 0:
                #         for aff in single_affiliations:
                #             institution = str(aff.split(';')[1]).strip()
                #             institution = re.sub('\sand$', '', institution).strip()
                #             institutions.append(institution)
                    
                # except:
                #     pass
                # single_affiliations = [x.strip() for x in single_affiliations if x != '']
                # single_affiliations = [x.replace(';',',') for x in single_affiliations]
                # single_affiliations = [x.rstrip(',') for x in single_affiliations]
                # print('**********************************************')
                # print('https://academic.oup.com'+article_link)
                # print(last_author_all_affiliations)
                # print(country)
                # print(institutions)
                # print('**********************************************')    
                

                # Get doi, date, and links 
                doi = article.css('.ww-citation-primary a::text').extract_first()
                
                date = article.css('.citation-date::text').extract_first()
                
                links= list(set([a.css('::attr("href")').extract_first() for a in article.css('.abstract a') if check_url(a)]))
                
                
                # This may work for some page types where the abstract is broken down into sub paragraphs...
                # such as motivation, results, supplementatry info, etc.
                # Continue below if page type is different 
                abstract = [[p.css('.title::text').extract_first(), ''.join(p.css(':not(.title)::text').extract()).strip()] for p in article.css('.abstract section')]
            
                # If abstract field returns empty, try other page types depending on journal type
                if journal_name=='bioinformatics':
                    if len(abstract)<1:
                        abstract=[]
                        all_sections = [' '.join(p.css('::text').extract()) for p in article.css('.abstract p')]
                        for p in all_sections:
                            p = p.split(': ', 1)
                            title = ''
                            body = ''
                            try:
                                title = p[0]
                                body = p[1]
                            except:
                                body = p[0]
                                title = 'Abstract'
                            abstract.append([title,body])
                if journal_name=='nar'or journal_name=='database':
                    if len(abstract)<1:
                        abstract= [["Abstract", ''.join(p.css('::text').extract())] for p in article.css('.abstract p')]
     
                # Add data to article dict
                articles['article_data'].append({
                    'article_title': article_title,
                    'authors': authors,
                    'last_author_affiliation': last_author_all_affiliations,
                    'doi': doi,
                    'abstract': abstract,
                    'date': date,
                    'links': links
                })
                
            # # Save data
            with open(outfile, 'w') as openfile:
                openfile.write(json.dumps(articles, indent=4))


