import xml.etree.ElementTree as ET
from Entry import Entry

def parseExportList(file):
    root = ET.parse(file).getroot()
    entries = []
    elements = root.findall('manga') + root.findall('anime')
    for element in elements:
        isManga = element.tag == 'manga'
        entry = _createEntryFromListing(element, isManga)
        if entry.score > 0:
           entries.append(entry)
    return entries


def _createEntryFromListing(element, isManga):
    score = int(element.find('my_score').text)
    prio = element.find('my_priority').text 
    if isManga:
        title = element.find('manga_title').text
        elem_id = element.find('manga_mangadb_id').text
    else:
        title = element.find('series_title').text
        elem_id = element.find('series_animedb_id').text
    # {elem_id}
    entry = Entry(elem_id, score, prio, title)
    return entry

