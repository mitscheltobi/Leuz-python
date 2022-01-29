import numpy as np

class entry:
  def __init__(self, ID: int, name: str, NAICE: list, totAssets: list, revenue: list)-> None:
    self.ID = ID
    self.name = name
    self.NAICE = NAICE
    self.totAssets = np.array(totAssets)
    self.laggedAssets = self.totAssets[1:]
    self.opRev = np.array(revenue)

  def delta(self, values):
    return np.diff(values)*-1

  def __str__(self):
    return f"""
{{
  'ID': {self.ID},
  'name': {self.name},
  'NACE': {self.NAICE},
  'totAssets': {self.totAssets},
  'opRev': {self.opRev},
  '_calc.laggedAssets': {self.laggedAssets}
}}"""

  def __repr__(self):
    return f"""
{{
  'ID': {self.ID},
  'name': {self.name},
  'NACE': {self.NAICE},
  'totAssets': {self.totAssets},
  'opRev': {self.opRev},
  '_calc.laggedAssets': {self.laggedAssets}
}}"""