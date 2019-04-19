#!/usr/bin/env python

from lxml import html
from pathlib import Path
import argparse
import configparser
import json
import math
import requests
import re
import sqlite3
import sys
import pickle
import datetime, time
# Constants
DECKS_PER_PAGE = 25.0
SAVE_FILE = 'WARLOCK_DECKS_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M') + '.pk'

HEADERS = {"Host": "www.hearthpwn.com",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
"Accept-Encoding": "gzip, deflate, br",
"Connection": "keep-alive",
"Cookie": "__cfduid=de551eba4aea375c580ca44316876ecc21555063367; ResponsiveSwitch.DesktopMode=1; _ga=GA1.2.849308507.1555063412; _gid=GA1.2.1571050046.1555063412; cdmgeo=cn; __gads=ID=970e4d5066de1b3f:T=1555063415:S=ALNI_MaHBHNuciT18igM1LRQClqvFK2v-Q; showPageBlock=1; AWSELB=19D9E15B16AC5892F871D598FB7CB8D50507BC0117F682FF66A4ADBB154C6B0D2AD439ABB04F85E38E6559C79F5EC35E7EB959235FCDFD181165608BE826717FD63059203F",
"Upgrade-Insecure-Requests": "1",
"Cache-Control": "max-age=0",
"TE": "Trailers"}

class Deck:

    """
    An object representing a single Hearthstone deck pulled from HearthPwn.
    """

    def __init__(self, deckid, hero, decktype, rating,
                 dust, updated, decklist):
        # returns (links, classes, types, ratings, dusts, epochs)
        """
        Initialize a HearthPwn Deck object.

        Parameters:

        - 'deckid'   - the HearthPwn ID number of the deck (as seen in the URL)
        - 'hero'     - the Hearthstone class of the deck
        - 'type'     - the deck type (midrange, tempo, control, etc)
        - 'rating'   - the HearthPwn deck rating
        - 'dust'     - dust required to craft deck
        - 'updated'  - epoch timestamp of last update
        - 'decklist' - a list of Card objects
        """

        self.deckid = int(deckid)
        self.hero = str(hero)
        self.type = str(decktype)
        self.rating = int(rating)
        self.dust = int(dust)
        self.updated = int(updated)
        if decklist is not None:
            self.decklist = decklist
        else:
            self.decklist = []

    def __repr__(self):
        output = str(self.deckid) + '\n'
        for card in self.decklist:
            output += str(card.amount) + ' ' + card.cardname + '\n'
        return output

    def get_length(self):
        """
        Return the number of cards in the Deck.

        Parameters:

        - 'self' - the Deck object calling this function
        """
        length = 0
        # Can't just do a count since you can have 1 or 2 of a card
        # in a given deck.
        for card in self.decklist:
            length += card.amount
        return length


class Card:

    """
    An object representing a card in a Hearthstone deck.
    """

    def __init__(self, cardname, amount):
        """
        Initialize a Hearthstone card object.

        Parameters:

        - 'cardname' - the text name of a Hearthstone card
        - 'amount' - the number of this card included in the parent deck
        """
        self.cardname = str(cardname)
        self.amount = int(amount)

    def __repr__(self):
        return str(self.amount) + 'x ' + self.cardname


class setting():
    def __init__(self):
        self.buildcollection = True
        self.builddecks = True
        self.perclass = True
        self.filtering = 'filter-show-standard=1&filter-deck-tag=1&filter-class=512'
        self.sorting = '-datemodified'
        self.count = None
        self.patch = 48


def main():
    print("Loading Argument Parser")
    args = setting()
    # print("Argument Parser Loaded")
    # print("Loading Config Parser")
    # config = build_configparser()
    # print("Config Parser Loaded")
    # operselected = (args.builddecks or args.buildcards or
    #                 args.buildcollection or args.results)
    # if not operselected:
    #     # TODO: Swap to actual Python error/exception handling?
    #     print('ERROR: You must use --builddecks, --buildcards,'
    #           ' and/or --buildcollection')
    #     argparser.print_help()
    #     sys.exit(-1)
    # auth_session = {"__cfduid":"de551eba4aea375c580ca44316876ecc21555063367",
    #                 "__gads":"ID=970e4d5066de1b3f:T=1555063415:S=ALNI_MaHBHNuciT18igM1LRQClqvFK2v-Q",
    #                 "_ga":	"GA1.2.849308507.1555063412",
    #                 "_gid":	"GA1.2.1571050046.1555063412",
    #                 "AWSELB":"19D9E15B16AC5892F871D598FB7CB8D50507BC01172E1C04701E62890539B08C35276EEA554F85E38E6559C79F5EC35E7EB959235FCDFD181165608BE826717FD63059203F",
    #                 "cdmgeo":"cn",
    #                 "ResponsiveSwitch.DesktopMode":"1"}
    #
    #
    # if args.buildcollection:
    #     print("Building collection database...")
    #     get_collect = get_collection(auth_session)
    decks = get_newdecks(args.filtering, args.sorting,
                      args.count, args.patch)
    save_decks(decks)
    # if args.builddecks:
    #     print("Building deck database...")
    #     # TODO: Consolidate this into one function call
    #     if args.perclass:
    #         decks = get_decks_per_class(args.filtering, args.sorting,
    #                                     args.count, args.patch)
    #     else:
    #         decks = get_decks(args.filtering, args.sorting,
    #                           args.count, args.patch)
    #     # populate_deck_db(decks, cursor)
    #
    #
    # decks = []
    #
    # if not args.count:
    #     # Substitute a default count in here so that all classes return the
    #     # same number of decks. The default count is 10% of the total decks
    #     # for the current filtering/sorting/patch.
    #     url = generate_url(args.filtering, args.sorting, args.patch)
    #     pagecount = get_pagecount(get_htmlelement_from_url(url))
    #     count = int((pagecount * DECKS_PER_PAGE * 0.1) / 1.0
    # decks += get_decks(args.filtering, args.sorting, args.count, args.patch)

    print('Complete!')


# def build_argparser():
#     """
#     Builds the argparser object with all of the arguments and help text.
#     """
#     desc = ("Scrape Hearthstone decks from HearthPwn (http://hearthpwn.com), "
#             "then build a SQLite database of the results. Can also scrape "
#             "card collection data from HearthPwn/Innkeeper "
#             "(http://innkeeper.com), and integrates with omgvamp's Mashape "
#             "Hearthstone API (http://hearthstoneapi.com) to build a table of "
#             "card data that can be used to make more advanced queries.")
#     parser = argparse.ArgumentParser(description=desc)
#     # parser.add_argument('--buildcards', action='store_true',
#     #                     help='build card database from Mashape')
#     parser.add_argument('--builddecks', action='store_true',
#                         help='build deck database from HearthPwn')
#     parser.add_argument('--buildcollection', action='store_true',
#                         help='build personal card collection from Hearthpwn')
#     # TODO: Possibly make this just a value passed in for --builddecks?
#     parser.add_argument('--perclass', action='store_true',
#                         help='get the same number of decks for each class')
#     parser.add_argument('--count', type=int,
#                         help='number of decks to retrieve (per class, if'
#                              ' --perclass is set)')
#     parser.add_argument('--filtering',
#                         help='the HearthPwn filter used when finding decks, '
#                              'as seen in the HearthPwn URL')
#     parser.add_argument('--sorting',
#                         help='the HearthPwn sorting used when finding '
#                              'decks, as seen in the HearthPwn URL after '
#                              '"&sort="')
#     parser.add_argument('--patch', type=int,
#                         help='the HearthPwn patch ID used when finding '
#                              'decks, as seen in the HearthPwn URL after '
#                              '"&filter-build="')
#     # parser.add_argument('--results', action='store_true',
#     #                     help='for all cards, '
#     #                          'display (in a CSV-ish format) the: '
#     #                          'cardname, '
#     #                          'hero (or neutral), '
#     #                          'total count of decks using the card, '
#     #                          'percentage of decks using the card, '
#     #                          'average count of the card in decks using it, '
#     #                          'and the count of the card in your collection.')
#     return parser


# def build_configparser():
#     """
#     Builds the configparser object, and creates any missing config,
#     saving the config.ini file when done.
#     """
#     # mashape_key = ''
#     # legacy_mashape_file = Path("./mashape_key.txt")
#     # if legacy_mashape_file.is_file():
#     #     mashape_key = legacy_mashape_file.read_text().strip()
#     #     print('Found legacy mashape_key.txt file.')
#     #     print('Read key: ' + mashape_key)
#     #     # We have the key from the legacy file. Remove it.
#     #     legacy_mashape_file.unlink()
#     config = configparser.ConfigParser()
#     config.read('config.ini')
#
#     configupdated = False
#     if not config.has_section('Configuration'):
#         print('Adding Configuraiton section to config.ini.')
#         config.add_section('Configuration')
#         configupdated = True
#     # if not config.has_option('Configuration', 'MashapeKey'):
#     #     print('MashapeKey does not exist in config.ini.')
#     #     if len(mashape_key) > 0:
#     #         print(' Adding value ' + mashape_key + '.')
#     #     else:
#     #         print(' Adding blank entry.')
#     #     config['Configuration']['MashapeKey'] = mashape_key
#         configupdated = True
#     if not config.has_option('Configuration', 'AuthSession'):
#         print('AuthSession does not exist in config.ini.')
#         print('Adding blank entry.')
#         config['Configuration']['AuthSession'] = ''
#         configupdated = True
#     if configupdated:
#         with open('config.ini', 'w') as configfile:
#             config.write(configfile)
#     return config

def save_decks(decks):
    with open(SAVE_FILE, "wb") as f:
        pickle.dump(decks, f)

def load_decks(file):
    with open(file, "rb") as f:
        data = pickle.load(f)
    return data

def get_newdecks(filtering=None, sorting=None, count=None, patch=None):
    """
    Retrieve Decks from HearthPwn as a list of Deck objects, ensuring the same
    number of decks are retrieved for each class..

    Parameters:

    - 'filtering' - the HearthPwn filter used when finding decks, as seen in
    the HearthPwn URL
    - 'sorting' - the HearthPwn sorting used when finding decks, as seen in the
    HearthPwn URL after "&sort="
    - 'count' - number of decks to retrieve
    - 'patch' - the HearthPwn patch ID used when finding decks, as seen in the
    HearthPwn URL after "&filter-build="
    """
    # HearthPwn assigns each class a "power of two" value for filtering by
    # class so that you can AND the values and filter by multiple classes.
    # Since we want to query each class individually (to get the same number
    # of results for each class), calculating powers of 2 works fine.
    # classes = [512]  # [2**x for x in range(2, 11)]
    # decks = []

    if not count:
        # Substitute a default count in here so that all classes return the
        # same number of decks. The default count is 10% of the total decks
        # for the current filtering/sorting/patch.
        url = generate_url(filtering, sorting, patch)
        pagecount = get_pagecount(get_htmlelement_from_url(url))
        count = int(pagecount * DECKS_PER_PAGE)

    decks = get_decks(filtering, sorting, count, patch)
    return decks


def get_decks_per_class(filtering=None, sorting=None, count=None, patch=None):
    """
    Retrieve Decks from HearthPwn as a list of Deck objects, ensuring the same
    number of decks are retrieved for each class..

    Parameters:

    - 'filtering' - the HearthPwn filter used when finding decks, as seen in
    the HearthPwn URL
    - 'sorting' - the HearthPwn sorting used when finding decks, as seen in the
    HearthPwn URL after "&sort="
    - 'count' - number of decks to retrieve
    - 'patch' - the HearthPwn patch ID used when finding decks, as seen in the
    HearthPwn URL after "&filter-build="
    """
    # HearthPwn assigns each class a "power of two" value for filtering by
    # class so that you can AND the values and filter by multiple classes.
    # Since we want to query each class individually (to get the same number
    # of results for each class), calculating powers of 2 works fine.
    classes = [512]  # [2**x for x in range(2, 11)]
    decks = []

    if not count:
        # Substitute a default count in here so that all classes return the
        # same number of decks. The default count is 10% of the total decks
        # for the current filtering/sorting/patch.
        url = generate_url(filtering, sorting, patch)
        pagecount = get_pagecount(get_htmlelement_from_url(url))
        count = int((pagecount * DECKS_PER_PAGE * 0.1) / len(classes))
    for classid in classes:
        decks += get_decks(filtering, sorting, count, patch, classid)
    return decks


def get_decks(filtering=None, sorting=None, count=None,
              patch=None, classid=None):
    """
    Retrieve Decks from HearthPwn as a list of Deck objects.

    Parameters:

    - 'filtering' - the HearthPwn filter used when finding decks, as seen in
    the HearthPwn URL
    - 'sorting' - the HearthPwn sorting used when finding decks, as seen in the
    HearthPwn URL after "&sort="
    - 'count' - number of decks to retrieve
    - 'patch' - the HearthPwn patch ID used when finding decks, as seen in the
    HearthPwn URL after "&filter-build="
    - 'classid' - the HearthPwn class ID used when finding decks, as seen in
    the HearthPwn URL after "&filter-class="
    """
    decks_metainfo = get_deck_metainfo(filtering, sorting, count,
                                       patch, classid)

    decks = []
    total = len(decks_metainfo)

    decklist = []
    for counter, deck in enumerate(decks_metainfo):
        print("Adding deck " + str(counter+1) + " of " + str(total))
        wait = True
        stime = 0
        trycount = 0
        while wait:
            time.sleep(stime)
            decklist = get_deck_list(deck[0])
            if decklist == []:
                stime += 0.5
                trycount += 1
                if trycount >20:
                    break
                continue
            wait = False
        if trycount > 20:
            continue
        decks += [Deck(deck[0], deck[1], deck[2], deck[3], deck[4], deck[5], decklist)]

    return decks


def get_deck_list(deckid):
    """
    For a given HearthPwn deck ID, return a list of Cards that belong to that
    deck.

    Parameters:

    - 'deckid' - a HearthPwn deck ID
    """
    # http://www.hearthpwn.com/decks/listing/ + deckid + /neutral or /class
    url = 'http://www.hearthpwn.com/decks/listing/'
    css = '#cards > tbody > tr > td.col-name'

    deck = []

    # Class Cards
    htmlelement = get_htmlelement_from_url(url + str(deckid) + '/class')
    cardelements = htmlelement.cssselect(css)
    # Neutral Cards
    htmlelement = get_htmlelement_from_url(url + str(deckid) + '/neutral')
    cardelements += htmlelement.cssselect(css)

    regex = re.compile('&#215;\s+(\d+)')
    for element in cardelements:
        # cssselect always returns an array, but in our case the result is
        # always just one element.
        cardname = element.cssselect('a')[0].text.strip()
        elementtext = html.tostring(element).decode('UTF-8')
        # There's probably a better way to get the amount, but we currently
        # look for the "x #" in the raw text of the element
        match = re.search(regex, elementtext)
        if match:
            amount = int(match.group(1))
        else:
            print('ERROR: Unable to get amount for card ' + cardname)
            # This shouldn't happen, but when it does, just continue on after
            # logging an error.
            amount = 0
        deck.append(Card(cardname, amount))

    return deck


def get_htmlelement_from_url(url):
    """
    Using requests and LXML's HTML module, retrieve a URL and return the page
    as an LXML HtmlElement.

    Parameters:

    - 'url' - the URL of the webpage to get
    """
    wait = True
    htmlelement = []
    while wait:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
        except:
            continue
        htmlelement = html.fromstring(response.text)
        if htmlelement == []:
            continue
        wait = False

    return htmlelement


def get_attributes_from_page(htmlelement, css, attribute):
    """
    Using LXML, get all of the attributes from a HtmlElement that match a css
    selector, and then return a list containing the contents of a given
    attribute for each element.

    Parameters:

    - 'htmlelement' - the HtmlElement containing elements to select from
    - 'css' - string containing the CSS selector
    - 'attribute' - string containing the attribute
    """
    elements = htmlelement.cssselect(css)
    attributes = [element.attrib[attribute] for element in elements]
    return attributes


def get_latest_patch():
    """
    Get the latest patch ID from HearthPwn
    """
    htmlelement = get_htmlelement_from_url('http://www.hearthpwn.com/decks')
    css = '#filter-build > option'
    patches = get_attributes_from_page(htmlelement, css, 'value')
    # Filtering out the empty/none result using list comprehension magic.
    patches = [patch for patch in patches if patch]
    patches.sort(key=int, reverse=True)
    return patches[0]


def get_pagecount(htmlelement):
    """
    Gets the total number of pages on a HearthPwn search from a htmlelement.
    """
    css = ('#content > section > div > div > div.listing-header >'
           'div.b-pagination.b-pagination-a > ul > li:nth-child(7) > a')
    pagecount = htmlelement.cssselect(css)[0].text
    print('Pagecount: ' + pagecount)
    return int(pagecount)


def generate_url(filtering=None, sorting=None, patch=None, classid=None):
    """
    Combines all factors used for sorting into a url.

    Default values are also substitued in here.

    Parameters:

    - 'filtering' - the HearthPwn filter used when finding decks, as seen in
    the HearthPwn URL
    - 'sorting' - the HearthPwn sorting used when finding decks, as seen in the
    HearthPwn URL after "&sort="
    - 'patch' - the HearthPwn patch ID used when finding decks, as seen in the
    HearthPwn URL after "&filter-build="
    - 'classid' - the HearthPwn class ID used when finding decks, as seen in
    the HearthPwn URL after "&filter-class="
    """
    # TODO: Rework this -- doesn't make sense to have default values but also
    # take into account the posibility of no value being present.
    if not filtering:
        # TODO: Complete documenting this default filtering
        # &filter-unreleased-cards=f - remove any unreleased cards
        # &filter-quality-free-max=29 - remove any decks with 30/all free cards
        filtering = ('filter-is-forge=2&filter-unreleased-cards=f'
                     '&filter-deck-tag=1&filter-deck-type-val=8'
                     '&filter-deck-type-op=4'
                     '&filter-quality-free-max=29')

    if not sorting:
        # Defaulting to sorting by decks with the most views
        sorting = '-viewcount'

    if not patch:
        patch = get_latest_patch()

    # To make things a bit easier on us, sorting, patch, and classid are all
    # compiled into the filtering.

    # Combine patch and filtering
    if patch and filtering:
        # This is separate from the filter attribute to make it easier to only
        # pull decks from the most recent patch.
        if filtering[-1] != '?' and filtering[-1] != '&':
            filtering += '&'
        filtering += 'filter-build=' + str(patch)
    elif patch:
        # Not currently used as filtering has a default above, but leaving just
        # in case I change how this works in the future.
        filtering = 'filter-build=' + str(patch)

    # Combine classid and filtering
    if classid and filtering:
        # This is separate from the filter attribute to make it easier to only
        # pull decks from a single class. This means we can, for example, get
        # the top 1000 decks from each class.
        if filtering[-1] != '?' and filtering[-1] != '&':
            filtering += '&'
        filtering += 'filter-class=' + str(classid)
    elif classid:
        filtering = 'filter-class=' + str(classid)

    # Combine sorting and filtering
    if sorting and filtering:
        if filtering[-1] != '?' and filtering[-1] != '&':
                filtering += '&'
        filtering += 'sort=' + sorting
    elif sorting:
        filtering = 'sort=' + sorting

    if filtering:
        url = 'http://www.hearthpwn.com/decks?' + filtering
    else:
        url = 'http://www.hearthpwn.com/decks'
    return url


def get_deck_metainfo(filtering=None, sorting=None, count=None,
                      patch=None, classid=None):
    """
    Gets a list of (links, classes, types, ratings, dusts, epochs)
    from HearthPwn using the provided paramters.

    Parameters:

    - 'filtering' - the HearthPwn filter used when finding decks, as seen in
    the HearthPwn URL
    - 'sorting' - the HearthPwn sorting used when finding decks, as seen in the
    HearthPwn URL after "&sort="
    - 'count' - number of decks to retrieve
    - 'patch' - the HearthPwn patch ID used when finding decks, as seen in the
    HearthPwn URL after "&filter-build="
    - 'classid' - the HearthPwn class ID used when finding decks, as seen in
    the HearthPwn URL after "&filter-class="
    """
    url = generate_url(filtering, sorting, patch, classid)

    if not count:
        # Get a 10% sampling of the pages for the current
        # filtering/sorting/patch/classid
        pagecount = get_pagecount(get_htmlelement_from_url(url))
        count = int(pagecount * .1)

    pagecount = math.ceil(count / DECKS_PER_PAGE)

    regex = re.compile('^\s*\/decks\/(\d+)')
    output = []
    # Adding one as range is exclusive
    for pagenum in range(1, int(pagecount)+1):

        # For each page, get a list of decks from all of the href attributes.
        # Then for each list of decks, pull out the deck ID using regex.
        # Finally, if there is a match, append the deck ID to the deckids list.
        page = ''
        if pagenum > 1:
            page = '&page=' + str(pagenum)

        htmlelement = get_htmlelement_from_url(url + page)

        # This CSS selector grabs all of the a (HTML hyperlink) elements in the
        # HearthPwn decks table (being specific to make sure we get the right
        # elements.) We can pull the deck IDs from the HREF attribute.
        css = '#decks > tbody > tr > td.col-name > div > span > a'
        links = htmlelement.cssselect(css)
        css = '#decks > tbody > tr > td.col-deck-type > span'
        decktypes = htmlelement.cssselect(css)
        css = '#decks > tbody > tr > td.col-class'
        heros = htmlelement.cssselect(css)
        css = '#decks > tbody > tr > td.col-ratings > div'
        ratings = htmlelement.cssselect(css)
        css = '#decks > tbody > tr > td.col-dust-cost'
        dusts = htmlelement.cssselect(css)
        css = '#decks > tbody > tr > td.col-updated > abbr'
        epochs = htmlelement.cssselect(css)

        links = [link.attrib['href'] for link in links]
        types = [decktype.text for decktype in decktypes]
        classes = [hero.text for hero in heros]
        ratings = [rating.text for rating in ratings]
        dusts = [dust.text.replace(",", "").replace("k", "00").replace(".", "")
                 for dust in dusts]
        epochs = [epoch.attrib['data-epoch'] for epoch in epochs]

        for x in range(len(links)):
            match = re.search(regex, links[x])
            links[x] = int(match.group(1))

        output += list(zip(links, classes, types, ratings, dusts, epochs))

    return output[:count]


def get_collection(auth_session):
    """
    Gets a list of all cards in your HearthPwn collection,
    and returns them as a json object.

    Parameters:

    - 'auth_session' - a string containing a HearthPwn Auth.Session cookie
    """
    if len(auth_session) <= 0:
        print('Auth Session does not exist in config.ini')
        sys.exit(-1)
    url = "http://www.hearthpwn.com/ajax/collection"
    cookies = auth_session
    response = requests.get(url, cookies=cookies)
    try:
        collection = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        print("Unable to decode (possibly empty) response.")
        print("Response: " + response.text)
        sys.exit(-1)
    return collection


if __name__ == "__main__":
    # Execute only if run as a script
    # a = load_decks("WARLOCK_DECKS_2019_04_13.pk")
    main()
