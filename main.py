import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import truncnorm
from xmlParser import parseExportList

def getCurrentDistribution(scores, showGraph = True):
    hist, bin_edges = np.histogram(scores, density=True)
    counts = getCountOfEachRanking(scores)

    if showGraph:
        plt.hist(scores, range=[1,10])
        plt.title('Current Ranking Distribution')
        plt.xlabel('Ranking')
        plt.ylabel('Number of Scores')
        plt.show()
    return counts

def getNormalizedDistribution(scores, showGraph = True):
    std, avg  = np.std(scores), np.mean(scores)
    samples = 1000000
    normalized_dist =  np.round(np.random.normal(avg, std, samples))
    temp = normalized_dist[ normalized_dist > 10 ].size
    normalized_dist = list (map(lambda x: 10 if x > 10 else 1 if x < 1 else np.round(x), normalized_dist))
    counts = getCountOfEachRanking(normalized_dist)

    counts = np.round(1.0 * len(scores) * counts / samples)

    if showGraph:
        normalizedScores = np.repeat(range(1, 11), counts.astype(int))
        plt.hist(normalizedScores, range=[1,10])
        plt.title('Normalized Ranking Distribution')
        plt.xlabel('Ranking')
        plt.ylabel('Number of Scores')
        plt.show()
    return counts


def printChangeMessage(diff):
    separator = '\n' + '-' * 55 + '\n'
    print (separator + 'Changes to make to normalize your ranking distribution:' + separator) 
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
    print ('\n')


def verifyTotalScores(scoreDistribution):
    totalPoints = 0
    for i in range(len(scoreDistribution)):
       totalPoints += (i+1) * scoreDistribution[i]
    return totalPoints

def getCountOfEachRanking(scores):
    unique, counts= np.unique(scores, return_counts=True)
    # we need to sanitize to ensure that all possible scores are represented.
    # if some number doesn't appear, we assign a count of 0
    rankings = range(1, 11)

    countDict = dict(zip(unique, counts))
    for r in rankings:
        if not r in countDict:
            countDict[r] = 0
    return np.array(list (map(lambda r: countDict[r], rankings)))

if __name__ == "__main__":
    file = sys.argv[1] if len(sys.argv) > 1 else "/Users/jdonerme/Downloads/mangalist_1610817958_-_10386609.xml"
    showGraph = True if len(sys.argv) > 2 else False

    entryList = parseExportList(file)
    # Sort
    entryList.sort(reverse=True)

    # get a list of all the scores
    scores = list (map(lambda x: x.score, entryList))

    std, avg  = np.round(np.std(scores), 3), np.round(np.mean(scores),3)
    print ("\nAverage Score: %s\nStandard Deviation of Scores: %s \n" %(avg, std))

    # get distributions
    curCounts = getCurrentDistribution(scores, showGraph)
    normalizedCounts = getNormalizedDistribution(scores, showGraph)
    normalizedCounts *= (1.0 * np.sum(curCounts) / np.sum(normalizedCounts))
    normalizedCounts = np.rint(normalizedCounts).astype(int)

    print ('Current Count of Each Ranking:')
    print curCounts

    print ('Count of Each Ranking in Normalized Distribution:')
    print (normalizedCounts)

    diff = normalizedCounts - curCounts

    print ('Difference Between Normalized Distribution Ranking Counts and Current Ranking Counts')
    print (diff)
    if (np.sum(diff) != 0):
        print ('Difference Between Number of Entries Rahnked for Normalized Distribution vs Current')
        print np.sum(diff)



    printChangeMessage(diff)
    
    # Print sorted list of entries
    # entryList = list (map(lambda x: x.__str__(), entryList))
    # print "'}\n{name: '".join(entryList)
    

    ## validation

    ## todo: replace ideal dist with truncated normal dist with https://stackoverflow.com/questions/41316068/truncated-normal-distribution-with-scipy-in-python
    verifyCur = verifyTotalScores(curCounts)
    verifyNormalized = verifyTotalScores(normalizedCounts)

    if (verifyCur != np.sum(scores)):
        print "Warning: The Sum of Scores for the Current Distribution is Wrong"
    
    if (verifyNormalized != verifyCur):
        print "Difference in the Total Number of Points Allocated by the Normal Distribution vs the Current Rankings"
        print verifyNormalized - verifyCur