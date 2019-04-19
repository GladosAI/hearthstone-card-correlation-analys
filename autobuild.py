from relatmatrix import RelatMat
from read_json import CardInfo
import numpy as np
from copy import deepcopy
import pickle
import datetime


class BDeck:
    cardinfo = None
    corrmat = None

    def __init__(self, dicklist: list, cardnum: int, score: float):
        self.dicklist = dicklist
        self._cardnum = cardnum
        self._score = score

    def __len__(self):
        return len(self.dicklist)

    def __lt__(self, other):
        return self.score < other.score

    def appid(self, idn: int):
        self._score = self._score + self._newscore(idn)
        self._cardnum = self._cardnum + self.cardinfo.id2cardmaxnum(idn)
        self.dicklist.append(idn)

    def _newscore(self, idn):
        newscore = 0.0
        for n, i in enumerate(reversed(self.dicklist), 1):
            s = self.corrmat.get_rmatrix[idn, i]
            newscore += s / n
        return newscore

    @property
    def cardnum(self):
        return self._cardnum

    @cardnum.setter
    def cardnum(self, value):
        self._cardnum = self._cardnum + value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = self._score + value


def recursion_trave(deck: BDeck, spreed, deep):
    if deep < 1:
        spreed = 30
    elif deep == 1:
        spreed = 20
    elif deep == 2:
        spreed = 10
    elif deep == 3:
        spreed = 10
    elif deep == 4:
        spreed = 10
    elif 5 <= deep <= 6:
        spreed = 5
    # elif deep == 6:
    #     #     spreed = 3
    elif 7 < deep <= 15:
        spreed = 3
    else:
        spreed = 1
    deep += 1
    # if deep > 3:
    #     return deck
    # print("deep:",deep)
    # print("spreed:", spreed)

    lastcard = deck.dicklist[-1]
    scope = RM.get_rmatrix[lastcard, :]
    scope[deck.dicklist] = 0
    scopesort = np.argsort(scope)[::-1]
    # sscope = np.argsort(scope) * (scope > 0)
    # scopesort = np.sort(scope)[::-1]
    # scopesort = scopesort[scopesort > 0]
    maxscoredeck = deck

    for i in range(spreed):
        # try:
        #     idnp = np.where(scope == scopesort[i])[0]
        # except IndexError:
        #     break
        if scope[scopesort[i]] > 0:
            idn = scopesort[i]
        else:
            break
        nextdeck = deepcopy(deck)
        nextdeck.appid(idn)

        if nextdeck.cardnum < 30:
            nextdeck = recursion_trave(nextdeck, spreed, deep)
        maxscoredeck = max(maxscoredeck, nextdeck)

    return maxscoredeck


def save_decks(decks):
    with open("bestdeck.pk", "wb") as f:
        pickle.dump(decks, f)


def load_decks(file):
    with open(file, "rb") as f:
        data = pickle.load(f)
    return data


if __name__ == '__main__':

    CI = CardInfo()
    bdeck = load_decks("bestdeck.pk")
    for ic in bdeck.dicklist:
        print(CI.id_map_card[ic]['name'])
    RM = RelatMat(CI)
    BDeck.cardinfo = CI
    BDeck.corrmat = RM

    Firstcard = 2
    Firstcard_num = CI.id2cardmaxnum(Firstcard)
    Firstscore = 0.0
    Firstdeck = BDeck([Firstcard], Firstcard_num, Firstscore)
    starttime = datetime.datetime.now()
    topdeck = recursion_trave(Firstdeck, 35, 0)
    endtime = datetime.datetime.now()
    print(endtime - starttime)
    save_decks(topdeck)
    pass
