import xml.etree.ElementTree as ET
import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import truncnorm


prioMap = {'High': 2, "Medium": 1, "Low": 0}

def mangaSort(m1, m2, includePrio=True):
    # rank by scores first
    if m1.score != m2.score or not includePrio:
        return m1.score > m2.score
    return prioMap[m1.prio] > prioMap[m2.prio]

def mangaSortScore(manga, includePrio=True):
    score = 10 * manga.score
    if (includePrio):
        score += prioMap[manga.prio]
    return score

class Manga(object):
    def __init__(self, idString, score, prio, title):
        self.id = idString
        self.score = score
        self.prio = prio
        self.title = title

    # formats the output when printing the song as a string
    def __str__(self):
        return u"%s (%s)".encode('utf-8').strip() % (self.title, self.id)

def mangaParse(mangeFile):
    root = ET.parse(file).getroot()
    mangaList = []
    # parse manga
    for mangaListing in root.findall('manga'):
        if mangaListing.tag != 'manga':
            continue
        # for mangaAttribute in mangaListing:
            # if mangaAttribute.tag == 'manga_title':
        title = mangaListing.find('manga_title').text
        score = int(mangaListing.find('my_score').text)
        prio = mangaListing.find('my_priority').text 
        manga_id = mangaListing.find('manga_mangadb_id').text
        {manga_id}
        if score > 0:
            entry = Manga(manga_id, score, prio, title)
            mangaList.append(entry)
    return mangaList

def getCurrentDistribution(scores, showGraph = True):
    hist, bin_edges = np.histogram(scores, density=True)
    unique, counts= np.unique(scores, return_counts=True)

    if showGraph:
        plt.hist(scores, bins=10)
        plt.title('current dist')
        plt.show()
    return counts

def getIdealizedHist(scores, showGraph = True):
    std, avg  = np.std(scores), np.mean(scores)
    samples = 1000000
    ideal_dist =  np.round(np.random.normal(avg, std, samples))
    temp = ideal_dist[ ideal_dist > 10 ].size
    ideal_dist = list (map(lambda x: 10 if x > 10 else 1 if x < 1 else np.round(x), ideal_dist))
    unique, counts= np.unique(ideal_dist, return_counts=True)

    counts = np.round(1.0 * len(scores) * counts / samples)


    print ("\navg: %s std: %s \n" %(avg, std))

    if showGraph:
        count, bins, ignored = plt.hist(ideal_dist, 10, range=[1,10])
        plt.title('idealized')
        plt.show()
    return counts


def printChangeMessage(diff):
    for i in range (len(diff)):
        quantifier = ''
        if (diff[i] > 0):
            quantifier = 'add'
        elif (diff[i] < 0):
            quantifier = 'subtract'
        else:
            continue
        plural = 's' if abs(diff[i]) != 1 else ''
        message = "%s %d score%s of %d " % (quantifier, abs(diff[i]), plural, i + 1)
        print (message)


def verifyTotalScores(scoreDistribution):
    totalPoints = 0
    for i in range(len(scoreDistribution)):
       totalPoints += (i+1) * scoreDistribution[i]
    return totalPoints

if __name__ == "__main__":
    file = sys.argv[1] if len(sys.argv) > 1 else "/Users/jdonerme/Downloads/mangalist_1610817958_-_10386609.xml"
    showGraph = True if len(sys.argv) > 2 else False

    mangaList = mangaParse(file)
    # Sort
    mangaList.sort(key=mangaSortScore, reverse=True)

    # get a list of all the scores
    scores = list (map(lambda x: x.score, mangaList))

    # get distributions
    curCounts = getCurrentDistribution(scores, showGraph)
    idealCounts = getIdealizedHist(scores, showGraph)
    idealCounts *= (1.0 * np.sum(curCounts) / np.sum(idealCounts))
    idealCounts = np.round(idealCounts)

    print ('current counts')
    print curCounts

    print ('ideal counts')
    print (idealCounts)

    diff = idealCounts - curCounts

    print ('difference')
    print (diff)
    print np.sum(diff)

    print ('\nchanges to make:')
    print ('-' * 25)

    printChangeMessage(diff)
    
    # mangaList = list (map(lambda x: x.__str__(), mangaList))
    # print "'}\n{name: '".join(mangaList)
    

    ## validation

    ## todo replace with https://stackoverflow.com/questions/41316068/truncated-normal-distribution-with-scipy-in-python
    verifyCur = verifyTotalScores(curCounts)
    verifyIdeal = verifyTotalScores(idealCounts)

    print np.sum(scores), verifyCur, verifyIdeal

    print np.sum(curCounts), np.sum(idealCounts)