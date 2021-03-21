
prioMap = {'High': 2, "Medium": 1, "Low": 0}

class Entry(object):
    def __init__(self, idString, score, prio, title):
        self.id = idString
        self.score = score
        self.prio = prio
        self.title = title

    def __cmp__(self, other):
        return cmp(getSortScore(self), getSortScore(other))

    # formats the output when printing the song as a string
    def __str__(self):
        return u"%s (%s)".encode('utf-8').strip() % (self.title, self.id)


## Sort entries based on score. Use Priority to tiebreak
def getSortScore(entry, includePrio=True):
    score = 10 * entry.score
    if (includePrio):
        score += prioMap[entry.prio]
    return score