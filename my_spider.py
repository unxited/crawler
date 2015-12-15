#!/usr/bin/python
# import unicodedata
import time
import urllib2

from bs4 import BeautifulSoup
from networkx import nx

maxPagesToVisit = 15000

url = "http://in.bgu.ac.il"
urls = [url]  # stack of urls to scrape
visited = set()
siteMapGraph = nx.DiGraph()


def bgu_spider(max_pages):
    page = 0
    while page < max_pages and len(urls) > 0:
        try:
            #print 'URL visited: ', urls[0]
            #r = requests.get(urls[0])
            #data = r.text

            data = urllib2.urlopen(urls[0]).read()

            visited.add(urls[0])

            siteMapGraph.add_node(urls[0])

            soup = BeautifulSoup(data)

        except:
#             print 'URL Not visited: ', urls[0]
            pass


        url = urls.pop(0) #TODO pop is the first one???
        page += 1
#         print 'Pages visited',              '-----====',  page,'=====-----'
        #print 'Pages in urls', len(urls)

        for link in soup.find_all('a', href=True):
            link = link.get('href')
            #temp = unicodedata.normalize('NFKD', link).encode('ascii','ignore')
            if link.endswith('pdf') or "jpg" in link:
                visited.add(link)
            elif "bgu.ac.il" in link:
                if link not in visited and link not in urls:
                    urls.append(link)
                    #print(link)  # TODO add this link to graph but not parse the wb page
            siteMapGraph.add_edge(url, link)

startTime = time.time()
bgu_spider(maxPagesToVisit)
totalTime=time.time()
print 'URLs visited: ' + len(visited)
if totalTime > 3600:
    print 'Time to visit ' + len(visited) + ' URLs: ' + str(float(totalTime)/3600) + ' Hours'
else:
    print 'Time to visit' + len(visited) +  'URLs: ', totalTime + ' seconds'