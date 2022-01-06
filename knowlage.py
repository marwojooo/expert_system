from experta import *

class Computer(Fact):
    """Fakty o komputerze"""

    pass


class BiosSignalAmi(Fact):
    """kody dźwiękowe biosu ami"""

    pass


class BiosSignalAwardAndPhenix(Fact):
    """kody dźwiękowe biosu award i phoenix award"""

    pass


class BiosSignalPhenix(Fact):
    """kody dźwiękowe biosu phoenix"""

    pass


class BiosAmiDiagnostic(KnowledgeEngine):
    pass
    # @Rule(BiosSignalAmi(code="-."))
    # def graphic_card_error(self):
    #     print("błąd karty graficznej")