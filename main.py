import requests
from newspaper import Article, article
import itertools
import lxml.html
from bs4 import BeautifulSoup
from db import DB
from pymongo import errors


# to export from mongodb :
# 1. CSV
# mongoexport --db SEARCH --collection python_search --csv --fields category,url,content --out python_search.csv
# 2. JSON
# mongoexport --db SEARCH --collection python_search --out python_search.json

# once can specify db name and collection if necessary
myDB = DB(collection="testpurpose")

"""
Number of words combinations : the more it is big the more combinations we have
and the more time it takes.
if we choose 3, the querystring will be composed
with 3 words from the words list + the mainSearchedWord
"""
numberOfCombination = 2

# small test
# myKeywords = { mainSearchWord_expectedCategory : [list of words that will be used as query for search engines]}
mainSearchedWord = "python"
myKeywords = {"python_reptile": ["reptile", "serpent"],
              "python_computer": ["langage", "linux", ]
              }

# takes more time :-)
# myKeywords = {"python_reptile": ["reptile", "serpent", "espèce", " Pythonidae", "Loxocemidae",
#                                  "scientifique", "genre", "écailles", "danger"],
#               "python_computer": ["langage", "linux", "syntaxe", "python2.7", "fonction",
#                                   "programmation", "informatique", "python3", "objet", "code" ]
#               }


def getContent(url):
    """
    Get the content of the url with newspaper3k module
    :param url: the given url
    :return the content of the url
    """
    art = Article(url)
    img_url = ""
    try:
        art.download()
        art.parse()
    except article.ArticleException:
        return None
    return art.text


def getResultJson(url, querystring):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'fr-FR,en;q=0.8',
           'Connection': 'keep-alive'}
    r = requests.request("GET", url, headers=hdr, params=querystring)
    return r.json()


def getResultText(url, querystring):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'fr-FR,en;q=0.8',
           'Connection': 'keep-alive'}
    r = requests.request("GET", url, headers=hdr, params=querystring)
    return r.text


def getQueryList(keywords):
    """
    Based on the words list and the constant *numberOfCombination*, the
    function returns all possible combinations
    :param keywords: list of keywords
    :return: all possible combinations
    """
    for i in itertools.combinations(keywords, numberOfCombination):
        yield ' '.join(map(str, i))


def getUrlFromSearchEngines(keywords, mySet):
    """
    Based on the words list, this function retrieve all the url
    from 3 different search engines (qwant, bing, google)
    :param keywords: list of keywords
    :param mySet: a set is used to avoid duplicated url
    :return: the number of found url
    """
    querystring = {"q": ""}
    for query in getQueryList(keywords):
        # the combination may not choose all the words in list, we force the mainSearchedWord
        querystring['q'] = query + " " + mainSearchedWord
        # Qwant
        rep = getResultJson(url_qwant, querystring)
        lenResponses = len(rep['data']['result']['items'])
        for i in range(0, lenResponses, 1):
            mySet.add(rep['data']['result']['items'][i]['url'])

        # Bing
        r = getResultText(url_bing, querystring)
        soup = BeautifulSoup(r, 'lxml')
        elements = soup.find_all(class_="b_algo")
        # elements = soup.find_all("a", class_="b_algo")
        for element in elements:
            mySet.add(element.find('a').get('href'))

        # Google
        r = getResultText(url_google, querystring)
        soup = BeautifulSoup(r, 'lxml')
        elements = soup.find_all(class_="rc")
        for element in elements:
            mySet.add(element.find('a').get('href'))
    return len(mySet)


def storeDB(urlSet, category):
    for link in urlSet:
        content = getContent(link)
        if content is not None:
            try:
                content.replace("\n", " ")
                content.replace("\r\n", " ")
            except error as e:
                print(e, link)
            else:
                entry = {"_id": link, "category": category,
                         "url": link, "content": content}
                myDB.updateSiteOne(entry)


url_qwant = "https://api.qwant.com/api/search/web/"
url_bing = "http://www.bing.com/search/"
url_google = "https://www.google.fr/search"

for category in myKeywords:
    urlSet = set()
    print(category, myKeywords[category])
    count = getUrlFromSearchEngines(myKeywords[category], urlSet)
    # print(urlSet)
    print("We retrieve *{}* urls for the category *{}* \nwith the following keywords : \n{}.".format(
        count, category, myKeywords[category]))
    storeDB(urlSet, category)
