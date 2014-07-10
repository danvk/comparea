iso3_to_url = None

import os
import re
import urllib
LINK_RE = re.compile(r'\[\[(.*?)\]\]')

def _extract_wiki_url(txt):
    m = LINK_RE.search(txt)
    if not m: return None

    brackets = m.group(1)
    wikiname = brackets.split('|')[0].replace(' ', '_')
    return 'http://en.wikipedia.org/wiki/%s' % urllib.quote(wikiname)


def _load_codes():
    global iso3_to_url
    iso3_to_url = {}
    p = os.path.join(os.path.dirname(__file__), 'countrycodes.wiki.txt')
    for line in file(p):
        parts = line.strip()[1:].split('||')  # strip leading '|'
        if len(parts) != 5: continue
        iso3 = parts[4]
        wikilink = parts[1]
        link = _extract_wiki_url(wikilink)

        if iso3 and link:
            iso3_to_url[iso3] = link

    # tweaks
    iso3_to_url['ALD'] = 'http://en.wikipedia.org/wiki/%C3%85land_Islands'
    iso3_to_url['PN1'] = iso3_to_url['PNG']  # papua new guinea
    iso3_to_url['KOS'] = 'http://en.wikipedia.org/wiki/Kosovo'
    iso3_to_url['CYN'] = 'http://en.wikipedia.org/wiki/Northern_Cyprus'
    iso3_to_url['PR1'] = iso3_to_url['PRT']  # portugal
    iso3_to_url['PSX'] = 'http://en.wikipedia.org/wiki/State_of_Palestine'
    iso3_to_url['SAH'] = 'http://en.wikipedia.org/wiki/Western_Sahara'
    iso3_to_url['SDS'] = 'http://en.wikipedia.org/wiki/South_Sudan'
    iso3_to_url['SOL'] = 'http://en.wikipedia.org/wiki/Somaliland'
    iso3_to_url['VGB'] = 'http://en.wikipedia.org/wiki/British_Virgin_Islands'
    iso3_to_url['ATC'] = 'http://en.wikipedia.org/wiki/Ashmore_and_Cartier_Islands'
    iso3_to_url['IOA'] = 'http://en.wikipedia.org/wiki/British_Indian_Ocean_Territory'
    iso3_to_url['KAS'] = 'http://en.wikipedia.org/wiki/Siachen_Glacier'


def iso3_to_wikipedia_url(iso3):
    global iso3_to_url
    if not iso3_to_url:
        _load_codes()
    return iso3_to_url.get(iso3, None)
