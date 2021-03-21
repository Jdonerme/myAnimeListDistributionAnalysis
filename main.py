import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import truncnorm
from xmlParser import parseExportList

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

    mangaList = parseExportList(file)
    # Sort
    mangaList.sort(reverse=True)

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