import numpy as np
import os
from read_json import CardInfo


class RelatMat:
    def __init__(self, cinfo, corrmode=False, diagzero=False):
        self.card = cinfo
        self.corrmode = corrmode
        self.diagzero = diagzero
        if corrmode:
            self.matrixfile = 'corrmatrix.npy'
        else:
            self.matrixfile = 'relatmatrix.npy'
        if os.path.exists(self.matrixfile):
            self.load_matrix()
            return
        n = len(self.card.id_map_card)
        self._r_matrix = np.zeros((n, n), np.int)

    def save_matrix(self):
        np.save(self.matrixfile, self._r_matrix)

    def load_matrix(self):
        self._r_matrix = np.load(self.matrixfile)
        if self.diagzero:
            maskeye = np.eye(self._r_matrix.shape[0], dtype=np.bool)
            self._r_matrix[maskeye] = 0

    def delt_matrix(self):
        if os.path.exists(self.matrixfile):
            os.remove(self.matrixfile)

    def find_value(self, r_index, c_index):
        return self._r_matrix[r_index, c_index]

    def change_value(self, r_index, c_index, value: int):
        self._r_matrix[r_index, c_index] = np.int(value)

    @property
    def get_rmatrix(self):
        return self._r_matrix


if __name__ == '__main__':
    cr = RelatMat(CardInfo())
    mx = cr.get_rmatrix
    cr.change_value(0, 0, 1)
    cr.find_value(0, 0)
    cr.save_matrix()
    mx = cr.get_rmatrix
    cr.delt_matrix()
