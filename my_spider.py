#!/usr/bin/python
# import unicodedata
import math
import time
import urllib2
from math import floor

import numpy as np
from bs4 import BeautifulSoup
from networkx import nx
from networkx.convert_matrix import to_numpy_matrix
from numpy.core.multiarray import count_nonzero

# from audioop import reverse

maxPagesToVisit = 3000
# np.outer
#np.dot

url = "http://in.bgu.ac.il"
urls = [url]  # stack of urls to scrape
visited = set()
siteMapGraph = nx.DiGraph()

#This function calculates and return the outcome of multiplying vector by matrix
def multi_vector_in_matrix(vector,matrix):
    size=int(vector.size)
    ansVector = np.empty(size)
    ansVector.fill(0)
    for i in range(size):
        for j in range(size):
            ansVector[i]+=matrix[j][:,i]*vector[j]
    return ansVector


#This function calculates and return the outcome of multiplying vector by vector
def multi_vector_in_vector(vecA,vecB):
    ans=0
    for i in range(vecA.size):
        ans+=vecA[i]*vecB[i]
    return ans


#This function calculates and return the norm between 2 vectors
def norm(vecA,vecB):
    ans=0
    for i in range(int(vecA.size)):
        ans+=pow(vecA[i]-vecB[i],2)
    return math.sqrt(ans)


#This function gathers URLs, links and build graph
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

            soup = BeautifulSoup(data,"html5lib")

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

            if "bgu.ac.il" in link and ("http://" or "https://") in link:
                if link not in visited and link not in urls:
                    urls.append(link)

                if link.endswith('pdf') or "jpg" in link:
                    visited.add(link)
                    #print(link)  # TODO add this link to graph but not parse the wb page
                if link != url:                                             # to prevent self-loops
                    siteMapGraph.add_edge(url, link)

# testM=np.matrix('1 2 3; 4 5 6; 7 8 9')
# testV=np.array([1,2,3])
# testResult = np.outer(testV, testM)
# result=multi_vector_in_matrix(testV, testM, 3)
# vecA=np.array([1,2,3])
# vecB=np.array([4,5,6])
# vevA=norm(vecA, vecB)
# vecB=1+vecA


startTime = time.time()
bgu_spider(maxPagesToVisit)

totalTime=time.time()-startTime
hours = floor(totalTime/3600)%3600
minutes = floor(totalTime/60)%60
seconds = totalTime - hours*3600 - minutes*60

if totalTime > 3600:
    print 'Time to visit ', str(len(visited)) + ' URLs:', str(int(hours)), 'Hours,', str(int(minutes)), 'Minutes,', str(int(seconds)),'Seconds\n'
elif totalTime > 60:
    print 'Time to visit' , str(len(visited)) + ' URLs:' , str(int(minutes)) + ' Minutes,',str(seconds),'Seconds\n'
else:
    print 'Time to visit' , str(len(visited)) +  ' URLs:', str(totalTime) + ' seconds\n'

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
pageRankV = np.empty(numOfNodes)                                                # initialize transition probabilities vector
pageRankV.fill(float(1)/numOfNodes)
#**************************************
# testSum=0
# for i in range(pageRankV.size):
#     testSum+=pageRankV[i]

#*********Generate matrix 'S'********
S = H.copy()
for i in range(numOfNodes):
    if a[i]==1:
        S[i]=float(1)/numOfNodes
#************************************

#*********Generate matrix 'E'********
E = S.copy()
E.fill(float(1)/numOfNodes)
#************************************

G = 0.85*S + 0.15*E                                                             # Generate matrix 'G'

print 'There are',np.count_nonzero(a),'non zero values in vector \'a\'\n'


print 'Difference between pageRank vectors (using \'G\' matrix):'
#*********Compute pageRank vector using 'G' matrix*****
i=1
startG = time.time()
while True:
    tempV = pageRankV
    pageRankV = multi_vector_in_matrix(pageRankV, G)
    normal = float(norm(tempV,pageRankV))
    print i, normal
    if normal < 0.001:                                                         # if smaller than threshold - quit
        break
    i+=1
#******************************************************
timeTook=time.time()-startG
hours = floor(timeTook/3600)%3600
minutes = floor(timeTook/60)%60
seconds = timeTook - hours*3600 - minutes*60

print 'Time took to calculate pageRank vector using \'G\':'
if timeTook > 3600:
    print str(int(hours)), 'Hours,', str(int(minutes)), 'Minutes,', str(seconds),'Seconds\n'
elif totalTime > 60:
    print  str(int(minutes)) + ' Minutes,',str(seconds),'Seconds\n'
else:
    print str(totalTime) + ' seconds\n'

#*****Print top 10 pageRanks and their probability******
# top10 = np.argsort(pageRankV)
# print 'Top 10 ranked pages:'
# listOfNodes=siteMapGraph.nodes()
# for i in range(pageRankV.size-1,pageRankV.size-11,-1):
#     index=top10[i]
#     print pageRankV.size-i,listOfNodes[index],'| p='+str(pageRankV[index])
#*******************************************************

pageRankV.fill(float(1)/numOfNodes)                                             # initialize pageRank vector
print 'Difference between pageRank vectors (using \'H\' matrix):'
#*********Compute pageRank vector using 'H' matrix*****
i=1
startH = time.time()
while True:
    tempV = pageRankV
    pageRankV = 0.85*multi_vector_in_matrix(pageRankV, H) + float(1)/numOfNodes*(0.85*multi_vector_in_vector(tempV, a)+0.15)
    normal = float(norm(tempV,pageRankV))
    print i, normal
    if normal < 0.001:                                                         # if smaller than threshold - quit
        break
    i+=1
#******************************************************
timeTook=time.time()-startH
hours = floor(timeTook/3600)%3600
minutes = floor(timeTook/60)%60
seconds = timeTook - hours*3600 - minutes*60

print 'Time took to calculate pageRank vector using \'H\':'
if timeTook > 3600:
    print str(int(hours)), 'Hours,', str(int(minutes)), 'Minutes,', str(seconds),'Seconds\n'
elif totalTime > 60:
    print  str(int(minutes)) + ' Minutes,',str(seconds),'Seconds\n'
else:
    print str(totalTime) + ' seconds\n'


#*****Print top 10 pageRanks and their probability******
top10 = np.argsort(pageRankV)
print 'Top 10 ranked pages:'
listOfNodes=siteMapGraph.nodes()
for i in range(pageRankV.size-1,pageRankV.size-11,-1):
    index=top10[i]
    print pageRankV.size-i,listOfNodes[index],'| p='+str(pageRankV[index])
#*******************************************************

print '\nURLs visited:', numOfNodes
print 'Links visited:' ,siteMapGraph.number_of_edges()
