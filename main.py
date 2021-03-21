import random, sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import truncnorm
from xmlParser import parseExportList

MAX_SCORE = 10
MIN_SCORE = 1

def usage():
    msg = "\nusage: python main.py MyAnimeListExportFile.xml (optionalGraphFlag)\n"
    print msg
def getCurrentDistribution(scores, showGraph = True):
    hist, bin_edges = np.histogram(scores, density=True)
    counts = getCountOfEachRanking(scores)

    if showGraph:
        plt.hist(scores, range=[MIN_SCORE, MAX_SCORE])
        plt.title('Current Ranking Distribution')
        plt.xlabel('Ranking')
        plt.ylabel('Number of Scores')
        plt.show()
    return counts

def getNormalizedDistribution(scores, showGraph = True):
    std, avg  = np.std(scores), np.mean(scores)
    samples = 1000000
    normalized_dist =  np.round(np.random.normal(avg, std, samples))
    normalized_dist = list (map(lambda x: MAX_SCORE if x > MAX_SCORE else MIN_SCORE if x < MIN_SCORE else np.round(x), normalized_dist))
    counts = getCountOfEachRanking(normalized_dist)

    numEntriesToRank = len(scores)
    counts = cleanNormalDistributionCounts(counts, numEntriesToRank, samples)

    if showGraph:
        normalizedScores = np.repeat(range(MIN_SCORE, MAX_SCORE + 1), counts.astype(int))
        plt.hist(normalizedScores, range=[MIN_SCORE, MAX_SCORE])
        plt.title('Normalized Ranking Distribution')
        plt.xlabel('Ranking')
        plt.ylabel('Number of Scores')
        plt.show()
    return counts

'''
    Since the normal dist entries are being generated randomly and then normalized,
    it is possible that the scores we generate won't exactly match the number of entries
    that should be scored.
    In that case, we add / subtract values from the distribution as needed.
'''
def cleanNormalDistributionCounts(rawScores, numEntriesToRank, samplesGenerated):
    counts = np.round(1.0 * numEntriesToRank * rawScores / samplesGenerated)
    countDifference = numEntriesToRank - np.sum(counts)

    scoreDist = np.repeat(range(MAX_SCORE - MIN_SCORE + 1), rawScores.astype(int))
    # if we need to rank more entries
    while countDifference > 0:
        scoreToAdd = random.choice(scoreDist)
        counts[scoreToAdd] += 1
        countDifference -= 1
    # if we've ranked too many entries
    while countDifference < 0:
        scoreToDrop = random.choice(scoreDist)
        counts[scoreToDrop] -= 1
        countDifference += 1
    return counts



'''
    Iterate through differences betwee nhe normal distribution and the current
    distribution to print a list of instructions for change scores to match the
    normal distribution
'''
def findScoresToChange(curCounts, normalizedCounts):
    separator = '\n' + '-' * 55 + '\n'
    print (separator + 'Changes to make to normalize your ranking distribution:' + separator)
    total_offset = 0
    differencesToFix = normalizedCounts - curCounts
    if (np.sum(differencesToFix) != 0):
        return
    changeMap = np.empty((10, 10)).astype(int)

    # for all values that may need to be changed
    for i in range(len(curCounts)):

        # look for changes 1 index at a time
        while ( np.sign(differencesToFix[i]) != 0):
            direction = np.sign(differencesToFix[i])

            # for all higher ratiings that we're still allowed to change
            for j in range(i + 1, len(curCounts)):
                # If the change needed for this ranking is the opposite as from the previous
                if -1 * direction * differencesToFix[j] > 0:
                    if direction > 0:
                        changeMap[j][i] += 1
                    else :
                        changeMap[i][j] += 1
                    differencesToFix[j] += direction
                    differencesToFix[i] += -1 * direction
                    break

    changes = np.argwhere(changeMap > 0)
    for change in changes:
        numChanges = changeMap[change[0]][change[1]]
        if numChanges > 10000 or numChanges < 0:
            # handle numpy prevision errors
            continue

        print ("Change %s Ranking(s) of %d to a %d" % (numChanges, change[0] + 1, change[1] + 1))
    print separator

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
    rankings = range(MIN_SCORE, MAX_SCORE + 1)

    countDict = dict(zip(unique, counts))
    for r in rankings:
        if not r in countDict:
            countDict[r] = 0
    return np.array(list (map(lambda r: countDict[r], rankings)))

if __name__ == "__main__":
    if not len(sys.argv) > 1:
        usage()
        exit()
    file = sys.argv[1]
    showGraph = True if len(sys.argv) > 2 else False

    try:
        entryList = parseExportList(file)
    except:
        usage()
        exit()
    
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
        print ('2349034') * 25



    printChangeMessage(diff)

    findScoresToChange(curCounts, normalizedCounts)
    
    # Print sorted list of entries
    # entryList = list (map(lambda x: x.__str__(), entryList))
    # print "'}\n{name: '".join(entryList)
    

    ## validation
    verifyCur = verifyTotalScores(curCounts)
    verifyNormalized = verifyTotalScores(normalizedCounts)

    if (verifyCur != np.sum(scores)):
        print "Warning: The Sum of Scores for the Current Distribution is Wrong"
    
    if (verifyNormalized != verifyCur):
        print "Difference in the Total Number of Points Allocated by the Normal Distribution vs the Current Rankings"
        print verifyNormalized - verifyCur