#!/usr/bin/python
# import unicodedata
import time
import urllib2

import numpy as np
from bs4 import BeautifulSoup
from networkx import nx
from networkx.convert_matrix import to_numpy_matrix
from numpy.core.multiarray import count_nonzero

maxPagesToVisit = 1

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


        url = urls.pop(0)
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
            if link != url:                                                     # to prevent self-loops
                siteMapGraph.add_edge(url, link)

startTime = time.time()
bgu_spider(maxPagesToVisit)
totalTime=time.time()-startTime

numOfNodes = siteMapGraph.number_of_nodes()
a = np.zeros(numOfNodes)                                                        # Initialize

# e = np.empty(numOfNodes)
# e.fill(1)

#*********Generate matrix 'H' and vector 'a'***
H = to_numpy_matrix(siteMapGraph)
for i in range(numOfNodes):
    nonzero=count_nonzero(H[i])
    if nonzero > 0:
        H[i] /= nonzero                                                         # initialize each row for equal transition probability
    if not H[i].all(0).any(True):
        a[i] = 1
#**********************************************

#**********Generate pageRank vector****
pageRankV = np.empty(numOfNodes)                                                # transition vector
pageRankV.fill(float(1)/numOfNodes)
#**************************************

#*********Generate matrix 'S'********
S = H.copy()
for i in range(numOfNodes):
    if a[i]==1:
        S[i]=float(1)/numOfNodes
#************************************

E = S.copy()
E.fill(1)

G = 0.85*S + 0.15*E                                                             # Generate matrix 'G'

print 'There are',np.count_nonzero(a),'non zero values in vector \'a\''

# print H[11][:,12]

print 'URLs visited:', numOfNodes
print 'Links visited:' ,siteMapGraph.number_of_edges()
if totalTime > 3600:
    print 'Time to visit' , str(len(visited)) + ' URLs:' , str(float(totalTime)/3600) + ' Hours'
elif totalTime > 60:
    print 'Time to visit' , str(len(visited)) + ' URLs:' , str(float(totalTime)/60) + ' Minutes'
else:
    print 'Time to visit' , str(len(visited)) +  ' URLs:', str(totalTime) + ' seconds'