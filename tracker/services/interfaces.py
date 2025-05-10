from abc import ABC, abstractmethod

class IProductService(ABC):
    @abstractmethod
    def save_product(self, data): pass

class IHTMLParser(ABC):
    @abstractmethod
    def parse(self, soup): pass
