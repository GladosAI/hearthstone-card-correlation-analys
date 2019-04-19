from read_json import CardInfo
from hearthpwn.hearth import Deck, Card, load_decks
import numpy as np
import os

DeckFile = ".\hearthpwn\WARLOCK_DECKS_2019_04_17_08_43.pk"


class DeckAnaly:
    def __init__(self, cardinfo):
        self.cardinfo = cardinfo()
        self.iddecks = []

        if os.path.exists('corrmatrix.npy'):
            self.load_matrix()
            return
        self.corrmat = None

    def save_matrix(self):
        np.save('corrmatrix.npy', self.corrmat)

    def load_matrix(self):
        self.corrmat = np.load('corrmatrix.npy')

    def main(self, decks: list):
        self.deck2iddeck(decks)
        self.decksrelat()
        self.cardrelat()
        self.save_matrix()

    def deck2iddeck(self, decks: list, compflag=True):
        iddecks = []
        for deck in decks:
            iddeck = []
            if deck.decklist == []:
                continue
            if len(deck.decklist) < 15 and compflag:
                continue
            for card in deck.decklist:
                cid = self.cardinfo.enname2id[card.cardname]
                iddeck.append(cid)
            iddecks.append(iddeck)

        self.iddecks = iddecks

    def decksrelat(self, threshold=0.8):
        print('all orign decks:', len(self.iddecks))
        filter_decks = []
        for n, i in enumerate(self.iddecks[:-1]):
            for j in self.iddecks[n+1:]:
                relaty = word_sim(i, j)
                if relaty > threshold:
                    if len(i) <= len(j):
                        i = False
                        break
            if i:
                filter_decks.append(i)
        print('now all decks:', len(filter_decks))
        self.iddecks = filter_decks

    def cardrelat(self, model='easy'):
        deckslen = len(self.iddecks)
        cards_num = len(self.cardinfo.id_map_card)
        count_matrix = np.zeros((cards_num, cards_num), np.float)
        for deck in self.iddecks:
            for i in deck:
                for j in deck:
                    count_matrix[i, j] += 1
        if model == 'easy':
            self.corrmat = easycorr(count_matrix, cards_num)
        else:
            self.corrmat = pmicorr(count_matrix, cards_num, deckslen)


def easycorr(count_matrix, cards_num):
    for i in range(cards_num):
        for j in range(cards_num):
            if i == j:
                continue
            if count_matrix[i, i] < 1.0 or count_matrix[j, j] < 1.0:
                continue
            count_matrix[i, j] = count_matrix[i, j] / (count_matrix[i, i] + count_matrix[j, j] - count_matrix[i, j])

    count_matrix[count_matrix < 0] = 0.0
    maskeye = np.eye(cards_num, dtype=np.bool)
    maskeye_not = np.logical_not(maskeye)
    mask = np.logical_and(maskeye_not, count_matrix > 0.0)
    matmax = count_matrix[mask].max()
    count_matrix[mask] = 5.0 * count_matrix[mask] / matmax
    # count_matrix[maskeye] = 0.0
    # count_matrix = np.rint(count_matrix).astype(np.int)
    return count_matrix


def pmicorr(count_matrix, cards_num, deckslen):
    for i in range(cards_num):
        x = y = count_matrix[i, i]
        if x < 1.0:
            continue
        count_matrix[i, :] = count_matrix[i, :] / x
        count_matrix[:, i] = count_matrix[:, i] / y

    count_matrix = count_matrix * deckslen
    count_matrix[count_matrix > 0] = np.log2(count_matrix[count_matrix > 0])

    count_matrix[count_matrix < 0] = 0.0
    maskeye = np.eye(cards_num, dtype=np.bool)
    maskeye_not = np.logical_not(maskeye)
    mask = np.logical_and(maskeye_not, count_matrix > 0.0)
    matmax = count_matrix[mask].max()
    count_matrix[mask] = 5.0 * count_matrix[mask] / matmax
    count_matrix[maskeye] = 0.0
    count_matrix = np.rint(count_matrix).astype(np.int)
    return count_matrix


def word_sim(a: list, b: list):
    c = set(a) & set(b)
    sim = 2.0 * len(c) / (len(a) + len(b))
    return sim


if __name__ == '__main__':
    Decks = load_decks(DeckFile)
    DAN = DeckAnaly(CardInfo)
    DAN.main(Decks)
    # DAN.deck2iddeck(Decks, True)
    # DAN.decksrelat()
    # DAN.cardrelat()
    pass
