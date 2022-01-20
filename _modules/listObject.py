import numpy as np

class entry:
  def __init__(self, ID: int, name: str, NAICE: list, EBIT: list, NetIncome: list, totAssets: list, cash: list, totLiabilities: list, curLiabilities: list, taxPayable: list, Depreciation: list)-> None:
    # Metadata
    self.ID = ID
    self.name = name
    self.NAICE = NAICE
    # raw data
    self.EBIT = np.array(EBIT)
    self.NetIncome = np.array(NetIncome)
    self.totAssets = np.array(totAssets)
    self.cash = np.array(cash)
    self.totLiabilities = np.array(totLiabilities)
    self.curLiabilities = np.array(curLiabilities)
    self.taxPayable = np.array(taxPayable)
    self.Depreciation = np.array(Depreciation)
    # calculated attributes
    self.Accruals = (self.delta(self.totAssets) - self.delta(self.cash)) - (self.delta(self.totLiabilities) - self.delta(self.curLiabilities) - self.delta(self.taxPayable)) - self.Depreciation[:-1]
    self.CFO = self.EBIT[:-1] - self.Accruals
    # EM 1 - scaled by lagged total assets
    self.stdEBIT = np.nanstd(self.EBIT[:-1]/self.totAssets[1:])
    self.stdCFO = np.nanstd(self.CFO/self.totAssets[1:])
    # EM 2 - scaled by lagged total assets; 2020-2014!!
    self.deltaAccruals = self.delta(self.Accruals)/self.totAssets[1:-1]
    self.deltaCFO = self.delta(self.CFO)/self.totAssets[1:-1]
    # EM 3
    self.absAccruals = np.abs(self.Accruals)
    self.absCFO = np.abs(self.CFO)
    # EM 4 - scaled by lagged total assets
    NetIncScaled = self.NetIncome[:-1]/self.totAssets[1:]
    # keep scaled positive values as profits and negatives as losses 
    self.profits = NetIncScaled[NetIncScaled > 0]
    self.losses = NetIncScaled[NetIncScaled < 0]

  def delta(self, values):
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
  'stdEBIT': {self.stdEBIT},
  'stdCFO': {self.stdCFO},
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
  'stdEBIT': {self.stdEBIT},
  'stdCFO': {self.stdCFO},
  'deltaCFO': {self.deltaCFO},
  'deltaAccruals': {self.deltaAccruals}
}}"""