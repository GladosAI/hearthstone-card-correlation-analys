import json

Race_eng2ch = {'DEMON':"恶魔", "BEAST":"野兽", 'MECHANICAL':"机械", 'PIRATE':'海盗', 'MURLOC':'鱼人',
               'ELEMENTAL':'元素', 'TOTEM':'图腾', 'DRAGON':'龙', 'ALL':'全部'}

class CardInfo:
    def __init__(self):
        self.file = "cards.collectible.json"
        self.cardclass = ['WARLOCK', 'NEUTRAL']
        self.cardset_list = ['DALARAN', 'TROLL', 'BOOMSDAY', 'GILNEAS', 'EXPERT1', 'CORE']
        self._war_card = []
        self._neu_card = []
        self._all_card = []
        self._id_map_card = {}
        self._enname_map_jsid = {}
        self._jsid_map_zhname = {}
        self._enname_map_id = {}
        self.read_json()
        self.enname_map()
        self.enmane2id()


    def enname_map(self):
        with open("cards.collectible_EN.json", "r", encoding='utf-8') as f:
            origin_f = json.load(f)
        war_card = []
        neu_card = []
        for i in origin_f:
            if i['cardClass'] in self.cardclass:
                if i['set'] in self.cardset_list:
                    if i.get('cost', '') == '':
                        continue
                    # if i.get('race', '') != '':
                    #     i['race'] = Race_eng2ch[i['race']]
                    if i.get('flavor', '') != '':
                        i.pop('flavor')
                    if i['id'] == "BOT_401" or i["id"] == 'TRL_513':
                        print(i['name'])   #     'Weaponized Piñata'
                        print(i['name'] == 'Mosh\'ogg Enforcer')
                    if i['cardClass'] == 'WARLOCK':
                        war_card.append(i)
                    elif i['cardClass'] == 'NEUTRAL':
                        neu_card.append(i)
        allcard = war_card + neu_card
        self._enname_map_jsid = {i['name']:i['id'] for i in allcard}
        pass

    def read_json(self):
        with open("cards.collectible.json", "r", encoding='utf-8') as f:
            origin_f = json.load(f)

        for i in origin_f:
            if i['cardClass'] in self.cardclass:
                if i['set'] in self.cardset_list:
                    if i.get('cost', '') == '':
                        continue
                    if i.get('race', '') != '':
                        i['race'] = Race_eng2ch[i['race']]
                    if i.get('flavor', '') != '':
                        i.pop('flavor')

                    if i['cardClass'] == 'WARLOCK':
                        self._war_card.append(i)
                    elif i['cardClass'] == 'NEUTRAL':
                        self._neu_card.append(i)

        self._war_card = sorted(self._war_card, key=lambda x: x['cost'])
        self._neu_card = sorted(self._neu_card, key=lambda x: x['cost'])
        self._all_card = self._war_card + self._neu_card
        self._id_map_card = {i: cinfo for i, cinfo in enumerate(self._all_card)}
        self._jsid_map_id = {v['id']:k for k, v in self._id_map_card.items()}
        self._jsid_map_zhname = {i['id']: i['name'] for i in self._all_card}
        pass

    def enmane2id(self):
        for k, v in self._enname_map_jsid.items():
            self._enname_map_id[k] = self._jsid_map_id[v]

    @property
    def get_neu_card(self):
        return self._neu_card

    @property
    def get_war_card(self):
        return self._war_card

    @property
    def get_all_card(self):
        return self._all_card

    @property
    def id_map_card(self):
        return self._id_map_card

    @property
    def enname2jsid(self):
        return self._enname_map_jsid

    @property
    def jsid2zhname(self):
        return self._jsid_map_zhname

    @property
    def enname2id(self):
        return self._enname_map_id

    def id2cardmaxnum(self, idn):
        if self._id_map_card[idn]['rarity'] == 'LEGENDARY':
            return int(1)
        else:
            return int(2)



if __name__ == '__main__':
    card = CardInfo()
    idcard = card.id_map_card
    pass
