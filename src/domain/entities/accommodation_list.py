from typing import List
from src.domain.entities.accommodation import Accommodation


class AccommodationList:
    Accommodations = []

    def __init__(self, Accommodations: List[Accommodation]):
        self.Accommodations = Accommodations

    def get_accommodation(self, concessionaria, cliente: str, conta: str, local: str) -> Accommodation:
        def filtro(el: Accommodation):
            teve_teste = False
            if el.cliente and cliente:
                teve_teste = True
                if el.cliente != cliente:
                    return False

            if el.conta and conta:
                teve_teste = True
                if el.conta != conta:
                    return False

            if el.local and local:
                teve_teste = True
                if el.local != local:
                    return False

            return teve_teste

        for_debug = [x for x in self.Accommodations if x.concessionaria == concessionaria]
        for x in for_debug:
            if filtro(x):
                return x

        return None
