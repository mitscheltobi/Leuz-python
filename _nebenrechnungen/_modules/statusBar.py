class statusBar:
    def __init__(self, max_val: int, min_val: int = 0, size: int = 10) -> None:
        self.max_val = max_val
        self.size = size
        self.status = 0
        self.statusPerc = 0.00
        self.offset = abs(min_val)
    
    def __calcProgress(self):
        return round(self.status/(self.max_val+self.offset),2)

    def update(self, stat: int):
        self.status = stat + self.offset
        self.statusPerc = self.__calcProgress()
        tiles = round(self.statusPerc*self.size)
        print("["+"█"*tiles+"▒"*(self.size-tiles)+f"] {round(self.statusPerc*100)}%", end='\r')
        return True