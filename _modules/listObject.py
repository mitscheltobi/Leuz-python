import numpy as np

class entry:
  def __init__(self, ID: int, name: str, NAICE: list, EBIT: list, NetIncome: list, totAssets: list, cash: list, totLiabilities: list, curLiabilities: list, taxPayable: list, Depreciation: list)-> None:
    self.ID = ID
    self.name = name
    self.NAICE = NAICE
    self.EBIT = np.array(EBIT)
    self.NetIncome = np.array(NetIncome)
    self.totAssets = np.array(totAssets)
    self.cash = np.array(cash)
    self.totLiabilities = np.array(totLiabilities)
    self.curLiabilities = np.array(curLiabilities)
    self.taxPayable = np.array(taxPayable)
    self.Depreciation = np.array(Depreciation)
    self.Accruals = (self.delta(self.totAssets) - self.delta(self.cash)) - (self.delta(self.totLiabilities) - self.delta(self.curLiabilities) - self.delta(self.taxPayable)) - self.Depreciation[:-1]
    self.CFO = self.EBIT[:-1] - self.Accruals
    self.deltaCFO = self.delta(self.CFO)
    self.deltaAccruals = self.delta(self.Accruals)

  def delta(self, values):
    # returns delta values of
    return np.diff(values)*-1

  def __str__(self):
    return f"""
{{
  'ID': {self.ID},
  'name': {self.name},
  'NACE': {self.NAICE},
  'EBIT': {self.EBIT},
  'NetIncome': {self.NetIncome},
  'totAssets': {self.totAssets},
  'cash': {self.cash},
  'totLiabilities': {self.totLiabilities},
  'curLiabilities': {self.curLiabilities},
  'taxPayable': {self.taxPayable},
  'Depreciation': {self.Depreciation},
  'Accruals': {self.Accruals},
  'deltaCFO': {self.deltaCFO},
  'deltaAccruals': {self.deltaAccruals}
}}"""

  def __repr__(self):
      return f"""
{{
  'ID': {self.ID},
  'name': {self.name},
  'NACE': {self.NAICE},
  'EBIT': {self.EBIT},
  'NetIncome': {self.NetIncome},
  'totAssets': {self.totAssets},
  'cash': {self.cash},
  'totLiabilities': {self.totLiabilities},
  'curLiabilities': {self.curLiabilities},
  'taxPayable': {self.taxPayable},
  'Depreciation': {self.Depreciation},
  'Accruals': {self.Accruals},
  'deltaCFO': {self.deltaCFO},
  'deltaAccruals': {self.deltaAccruals}
}}"""