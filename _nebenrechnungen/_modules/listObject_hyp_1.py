import numpy as np

class entry:
  def __init__(self, ID: int, name: str, NAICE: list, totAssets: list, sales: list)-> None:
    self.ID = ID
    self.name = name
    self.NAICE = NAICE
    self.totAssets = np.array(totAssets)
    self.laggedAssets = self.totAssets[1:]
    self.sales = np.array(sales[:-1])
    self.salesScaled = self.sales / self.laggedAssets

  def delta(self, values):
    return np.diff(values)*-1

  def __str__(self):
    return f"""
{{
  'ID': {self.ID},
  'name': {self.name},
  'NACE': {self.NAICE},
  'totAssets': {self.totAssets},
  'sales': {self.sales},
  '_calc.laggedAssets': {self.laggedAssets},
  '_calc.salesScaled': {self.salesScaled}
}}"""

  def __repr__(self):
    return f"""
{{
  'ID': {self.ID},
  'name': {self.name},
  'NACE': {self.NAICE},
  'totAssets': {self.totAssets},
  'sales': {self.sales},
  '_calc.laggedAssets': {self.laggedAssets},
  '_calc.salesScaled': {self.salesScaled}
}}"""