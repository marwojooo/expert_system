import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

cpu_temperature = ctrl.Antecedent(np.arange(20, 120, 1), "CPU temperature")
gpu_temperature = ctrl.Antecedent(np.arange(20, 160, 1), "GPU temperature")
condition = ctrl.Consequent(np.arange(0, 100, 1), "condition")

condition.automf(5)

cpu_temperature["cold"] = fuzz.sigmf(cpu_temperature.universe, 35, -1 / 2)
cpu_temperature["cool"] = fuzz.trimf(cpu_temperature.universe, [0, 35, 55])
cpu_temperature["normal"] = fuzz.dsigmf(cpu_temperature.universe, 45, 1, 65, 0.4)
cpu_temperature["warm"] = fuzz.trapmf(cpu_temperature.universe, [55, 60, 70, 80])
cpu_temperature["hot"] = fuzz.trapmf(cpu_temperature.universe, [70, 80, 85, 90])
cpu_temperature["critical-hot"] = fuzz.trapmf(
    cpu_temperature.universe, [70, 100, 120, 120]
)

gpu_temperature["cold"] = fuzz.sigmf(gpu_temperature.universe, 35, -1 / 2)
gpu_temperature["cool"] = fuzz.trapmf(gpu_temperature.universe, [0, 35, 50, 72])
gpu_temperature["normal"] = fuzz.dsigmf(gpu_temperature.universe, 55, 0.7, 85, 0.5)
gpu_temperature["warm"] = fuzz.trapmf(gpu_temperature.universe, [80, 90, 100, 120])
gpu_temperature["hot"] = fuzz.trimf(gpu_temperature.universe, [90, 120, 130])
gpu_temperature["critical-hot"] = fuzz.trapmf(
    gpu_temperature.universe, [100, 130, 160, 160]
)

# cpu_temperature.view()
# gpu_temperature.view()
# condition.view()

rule1 = ctrl.Rule(cpu_temperature["critical-hot"], condition["poor"])
rule2 = ctrl.Rule(gpu_temperature["critical-hot"], condition["poor"])
rule3 = ctrl.Rule(
    cpu_temperature["hot"] & gpu_temperature["hot"], condition["poor"]
)
rule4 = ctrl.Rule(
    cpu_temperature["cold"] & gpu_temperature["normal"], condition["good"]
)
rule5 = ctrl.Rule(
    cpu_temperature["normal"] & gpu_temperature["cold"], condition["good"]
)
# rule4 = ctrl.Rule(cpu_temperature["cold"], condition["good"])
# rule5 = ctrl.Rule(gpu_temperature["cold"], condition["good"])
rule6 = ctrl.Rule(
    cpu_temperature["cold"] & gpu_temperature["hot"], condition["decent"]
)
rule7 = ctrl.Rule(
    cpu_temperature["hot"] & gpu_temperature["cold"], condition["average"]
)
rule8 = ctrl.Rule(
    cpu_temperature["hot"] & gpu_temperature["cold"], condition["average"]
)
rule9 = ctrl.Rule(
    (cpu_temperature["normal"] & gpu_temperature["normal"])
    | (cpu_temperature["cool"] & gpu_temperature["cool"]),
    condition["good"],
)
rule10 = ctrl.Rule(
    cpu_temperature["warm"] | gpu_temperature["warm"], condition["decent"]
)
rule11 = ctrl.Rule(
    cpu_temperature["critical-hot"] & gpu_temperature["warm"], condition["poor"]
)
rule12 = ctrl.Rule(
    cpu_temperature["hot"] & gpu_temperature["cool"], condition["mediocre"]
)
# rule1.view()

condition_ctrl = ctrl.ControlSystem(
    [
        rule1,
        rule2,
        rule3,
        rule4,
        rule5,
        rule6,
        rule7,
        rule8,
        rule9,
        rule10,
        rule11,
        rule12,
    ]
)
condition_sim = ctrl.ControlSystemSimulation(condition_ctrl)
