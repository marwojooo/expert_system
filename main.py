from random import choice
from experta import *
from knowlage import *
from system_info import *

from enum import Enum, IntEnum

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
from autoencoder import *
import tensorflow as tf

class Restarts(Enum):
    NIE = 1
    ZARAZ_PO_URUCHOMIENIU = 2
    PODCZAS_LADOWANIA_SYSTEMU = 3
    PODCZAS_ZWYKLEGO_UZYTKOWANIA = 4
    PODCZAS_DUZEGO_OBCIAZENIA = 5


class Bios(Enum):
    AMI = 1
    AWARD = 2
    PHOENIX = 3


class BiosAmi(Enum):
    _1_KROTKI = 1
    _2_KROTKI = 2
    _3_KROTKI = 3
    _4_KROTKI = 4
    _5_KROTKI = 5
    _6_KROTKI = 6
    _7_KROTKI = 7
    _8_KROTKI = 8
    _9_KROTKI = 9
    _10_KROTKI = 10
    _11_KROTKI = 11
    _1_DLUGI_2_KROTKI= 12
    _1_DLUGI_3_KROTKI= 13
    _1_DLUGI_8_KROTKI= 14


comunicats = {
    'p_starts_up': "Sprawdź zasilacz",
    'p_restarts': "Problem z plikami systemu lub dyskiem twardym",
    'p_przegrzewanie': "Problem z przegrzewaniem się podzespołów. Zalecana czynność: wymiana pasty termoprzewodzącej, wyczyszczenie komputera z kurzu.",
    'p_ram_problem': "Problem z pamięcią RAM. Zalecana czynność: wymiana pamięci RAM, sprawdzenie czy dobrze została zamontowana.",
    'p_cpu_problem': "Problem z procesorem. Zalecana czynność: wymiana procesora, sprawdzenie czy dobrze został zamontowany.",
    'p_gpu_problem': "Problem z kartą graficzną. Zalecana czynność: wymiana karty graficznej, sprawdzenie czy dobrze została zamontowana.",
    'p_data_problem': "Błąd pamieci CMOS. Zalecana czynność: wymiana baterii BIOS",
    'p_anomaly_problem': "Wykryto anomalię, przeskanuj system programem antywirusowym",
    'p_condition_problem': "Problem z kondycją komputera. Zalecana czynność: odinstalowanie niepotrzebnych aplikacji ",
}


class ComputerDiagnostic(BiosAmiDiagnostic):
    def __init__(self):
        super().__init__()
        self.p_starts_up = False
        self.p_restarts = False
        self.p_przegrzewanie = False
        self.p_ram_problem = False
        self.p_cpu_problem = False
        self.p_gpu_problem = False
        self.p_data_problem = False
        self.p_anomaly_problem = False
        self.p_condition_problem = False

    @Rule(NOT(Computer(starts_up=True)))
    def computer_starts_up(self):
        self.p_starts_up = True

    @Rule(
        Computer(starts_up=True), Computer(restarts=Restarts.PODCZAS_LADOWANIA_SYSTEMU)
    )
    def computer_restart(self):
        self.p_restarts = True

    @Rule(
        OR(
            AND(
                Computer(restarts=Restarts.PODCZAS_ZWYKLEGO_UZYTKOWANIA),
                Computer(gpu_temp=P(lambda x: x >= 90)),
                Computer(cpu_temp=P(lambda x: x >= 70)),
            ),
            Computer(wentylacja=True),
        )
    )
    def przegrzewanie(self):
        self.p_przegrzewanie = True

    @Rule(
        AND(
            Computer(starts_up=True),
            Computer(restarts=Restarts.ZARAZ_PO_URUCHOMIENIU),
            OR(
                BiosSignalAmi(signal=BiosAmi._1_KROTKI),
                BiosSignalAmi(signal=BiosAmi._2_KROTKI),
                BiosSignalAmi(signal=BiosAmi._3_KROTKI),
            ),
        )
    )
    def ram_problem(self):
        self.p_ram_problem = True

    @Rule(
        AND(
            Computer(starts_up=True),
            Computer(restarts=Restarts.ZARAZ_PO_URUCHOMIENIU),
            OR(
                BiosSignalAmi(signal=BiosAmi._5_KROTKI),
            ),
        )
    )
    def cpu_problem(self):
        self.p_cpu_problem = True

    @Rule(
        AND(
            Computer(starts_up=True),
            Computer(restarts=Restarts.ZARAZ_PO_URUCHOMIENIU),
            OR(
                BiosSignalAmi(signal=BiosAmi._8_KROTKI),
                BiosSignalAmi(signal=BiosAmi._1_DLUGI_2_KROTKI),
                BiosSignalAmi(signal=BiosAmi._1_DLUGI_3_KROTKI),
                BiosSignalAmi(signal=BiosAmi._1_DLUGI_8_KROTKI),
            ),
        )
    )
    def gpu_problem(self):
        self.p_gpu_problem = True
    @Rule(
        OR(
            BiosSignalAmi(signal=BiosAmi._10_KROTKI),
            Computer(data=True),
        )
    )
    def data_problem(self):
        self.p_data_problem = True

    @Rule(
        Computer(anomaly_evaluate=P(lambda x: x >= 0.01)),
    )
    def anomaly_problem(self):
        self.p_anomaly_problem = True

    @Rule(
        Computer(condition=P(lambda x: x <= 65)),
    )
    def condition_problem(self):
        self.p_condition_problem = True
def print_system_data(system_info: SystemInfo, cpu_temp, gpu_temp):
    print("CPU usage:", system_info.cpu_usage)
    print("CPU temp:", cpu_temp, "C")
    print("########################################")
    print("GPU usage:", system_info.gpu_usage)
    print("GPU temp:", gpu_temp, "C")
    print("########################################")
    print("Memory usage:", system_info.memory_usage)
    print("Disk speed:", system_info.disk_usage / (1024 * 1024 * interval), "MB/s")
    print(
        "Network speed:", system_info.network_usage / (1024 * 1024 * interval), "MB/s"
    )


def get_input(dict):
    print("Czy komputer się uruchamia? y/n: ")
    selection = input()
    if selection == "y":
        dict["starts_up"] = True
    else:
        dict["starts_up"] = False

    print("Czy komputer wydaje sygnały dźwiękowe podczas uruchamiania? y/n: ")
    selection = input()
    if selection == "y":
        dict["signal"] = True
        print("Jaki jest rodzaj biosu? 1/2/3: ")
        print("1) AMI")
        print("2) AWARD lub PHOENIX AWARD")
        print("3) PHOENIX")
        selection = int(input())
        dict["bios"] = Bios(selection)
        if dict["bios"] == Bios.AMI:
            print("Ile razy pika komputer: ")
            for e in BiosAmi:
                print(e.value,")",e.name)
            dict["signal_type"] = BiosAmi(int(input()))
    else:
        dict["signal"] = False

    print("Czy komputer się restartuje?")
    print("1) nie")
    print("2) zaraz po uruchomieniu")
    print("3) podczas ładowania systemu")
    print("4) podczas zwykłego użytkowania")
    print("5) podczas dużego obciążenia")
    selection = input()
    selection = int(selection)
    if selection in range(5):
        dict["restarts"] = Restarts(int(selection))
    else:
        print("niepoprawna wartość")
        dict["restarts"] = Restarts.NIE

    print("Czy wyświetla się obraz na monitorze? y/n: ")
    selection = input()
    if selection == "y":
        dict["monitor"] = True
    else:
        dict["monitor"] = False

    print("Czy wentylacja komputera jest głośniejsza niż normalnie? y/n: ")
    selection = input()
    if selection == "y":
        dict["wentylacja"] = True
    else:
        dict["wentylacja"] = False

    print(
        "Czy po każdym wyłączeniu komputera ustawiona data i godzina resetuje się do domyślnej? y/n: "
    )
    selection = input()
    if selection == "y":
        dict["data"] = True
    else:
        dict["data"] = False


if __name__ == "__main__":
    system_dict = {}
    system_info = SystemInfo()
    system_info.get_data()
    cpu_temp = 80
    gpu_temp = 90
    boot_time = 7

    print_system_data(system_info, cpu_temp, gpu_temp)
    get_input(system_dict)
    system_dict["cpu_temp"] = cpu_temp
    system_dict["gpu_temp"] = gpu_temp
    system_dict["boot_time"] = boot_time

    system_dict["cpu_usage"] = system_info.cpu_usage
    system_dict["network_usage"] = system_info.network_usage / (1024 * 1024 * interval)
    system_dict["disk_usage"] = system_info.disk_usage / (1024 * 1024 * interval)
    system_dict["gpu_usage"] = system_info.gpu_usage
    system_dict["memory_usage"] = system_info.memory_usage

    # print(system_dict)

    engine = ComputerDiagnostic()
    engine.reset()
    engine.declare(
        Computer(
            starts_up=system_dict["starts_up"],
            restarts=system_dict["restarts"],
            cpu_temp=system_dict["cpu_temp"],
            gpu_temp=system_dict["gpu_temp"],
            wentylacja=system_dict["wentylacja"],
            monitor=system_dict["monitor"],
            data=system_dict["data"],
        )
    )
    if system_dict["signal"]:
        if system_dict["bios"] == Bios.AMI:
            engine.declare(BiosSignalAmi(signal=system_dict["signal_type"]))

    ########################################
    from fuzzysets import *
    condition_sim.input["CPU temperature"] = system_dict["cpu_temp"]
    condition_sim.input["GPU temperature"] = system_dict["gpu_temp"]

    condition_sim.compute()
    # cpu_temperature.view(sim=condition_sim)
    # condition.view(sim=condition_sim)

    condition = condition_sim.output['condition']

    engine.declare(
        Computer(
            condition=condition
        )
    )
    # print(condition)
    plt.show()
    #########################################
    autoencoder = load_model()
    autoencoder.load_weights("models/tr")
    
    #dat = s.SystemInfo(20, 50, 1000, 10000, 0).get_params()
    dat = system_info.get_params()
    evaluate = autoencoder.evaluate([dat], [dat])
    print(evaluate)
    engine.declare(
        Computer(
            anomaly_evaluate=evaluate
        )
    )

    engine.run()
    if(engine.p_przegrzewanie):
        print(comunicats['p_przegrzewanie'])
    if(engine.p_ram_problem):
        print(comunicats['p_ram_problem'])
    if(engine.p_restarts):
        print(comunicats['p_restarts'])
    if(engine.p_starts_up):
        print(comunicats['p_starts_up'])
    if(engine.p_cpu_problem):
        print(comunicats['p_cpu_problem'])
    if(engine.p_gpu_problem):
        print(comunicats['p_gpu_problem'])
    if(engine.p_data_problem):
        print(comunicats['p_data_problem'])
    if(engine.p_anomaly_problem):
        print(comunicats['p_anomaly_problem'])
    if(engine.p_condition_problem):
        print(comunicats['p_condition_problem'])