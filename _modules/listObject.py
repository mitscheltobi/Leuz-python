import numpy as np

class entry:
  def __init__(self, ID: int, name: str, NAICE: list, EBIT: list, NetIncome: list, totAssets: list, totCurAssets: list, cash: list, totLiabilities: list, curLiabilities: list, shortTermDebt: list, taxPayable: list, Depreciation: list)-> None:
    self.ID = ID
    self.name = name
    self.NAICE = NAICE
    self.EBIT = np.array(EBIT)
    self.NetIncome = np.array(NetIncome)
    self.totAssets = np.array(totAssets)
    self.totCurAssets = np.array(totCurAssets)
    self.cash = np.array(cash)
    self.totLiabilities = np.array(totLiabilities)
    self.curLiabilities = np.array(curLiabilities)
    self.shortTermDebt = np.array(shortTermDebt)
    self.taxPayable = np.array(taxPayable)
    self.Depreciation = np.array(Depreciation)
    # calculated attributes
    self.Accruals = (self.delta(self.totCurAssets) - self.delta(self.cash)) - (self.delta(self.curLiabilities) - self.delta(self.shortTermDebt) - self.delta(self.taxPayable)) - self.Depreciation[:-1]
    self.CFO = self.EBIT[:-1] - self.Accruals
    # EM 1 - scaled by lagged total assets; timeframe = yearsSupplied - 1
    ebitScaled = self.EBIT[:-1]/self.totAssets[1:]
    assetsScaled = self.CFO/self.totAssets[1:]
    self.stdEBIT = np.nanstd(ebitScaled)
    self.stdCFO = np.nanstd(assetsScaled)
    # EM 2 - scaled by lagged total assets; timeframe = yearsSupplied - 2 beacuase accruals = yearsSupplied - 1, deltaAccruals = yearsSupplied - 2
    self.deltaAccruals = self.delta(self.Accruals)/self.totAssets[1:-1]
    self.deltaCFO = self.delta(self.CFO)/self.totAssets[1:-1]
    # EM 3 remove the last year to bring EM measures to same timeframe; timeframe = yearsSupplied - 2
    self.absAccruals = np.abs(self.Accruals[:-1])
    self.absCFO = np.abs(self.CFO[:-1])
    # EM 4 - scaled by lagged total assets; remove the last year to bring EM measures to same timeframe; timeframe NetIncomeScaled = yearsSupplied - 1
    NetIncScaled = self.NetIncome[:-1]/self.totAssets[1:]
    # keep scaled positive values as profits and negatives as losses 
    self.profits = [x for x in NetIncScaled[:-1] if x > 0]
    self.losses = [x for x in NetIncScaled[:-1] if x < 0]

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
  'curAssets': {self.totCurAssets},
  'cash': {self.cash},
  'totLiabilities': {self.totLiabilities},
  'curLiabilities': {self.curLiabilities},
  'shortTermDebt': {self.shortTermDebt},
  'taxPayable': {self.taxPayable},
  'Depreciation': {self.Depreciation},
  'Accruals': {self.Accruals},
  'CFO': {self.CFO}
  'stdEBIT': {self.stdEBIT},
  'stdCFO': {self.stdCFO},
  'deltaCFO': {self.deltaCFO},
  'deltaAccruals': {self.deltaAccruals},
  'profits': {self.profits},
  'losses': {self.losses}
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
  'curAssets': {self.totCurAssets},
  'cash': {self.cash},
  'totLiabilities': {self.totLiabilities},
  'curLiabilities': {self.curLiabilities},
  'shortTermDebt': {self.shortTermDebt},
  'taxPayable': {self.taxPayable},
  'Depreciation': {self.Depreciation},
  'Accruals': {self.Accruals},
  'CFO': {self.CFO}
  'stdEBIT': {self.stdEBIT},
  'stdCFO': {self.stdCFO},
  'deltaCFO': {self.deltaCFO},
  'deltaAccruals': {self.deltaAccruals},
  'profits': {self.profits},
  'losses': {self.losses}
}}"""