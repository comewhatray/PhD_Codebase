import os

# configName = "scale_x1_y6_BestResults_0.7-membership_0.7-rhythm_ins_1_del_0.json"
configName = "-membership_0.9-rhythm_ins_0.4_del_0.4_TEST.json"
configDirectory = "CoreConfigurations/Paper2Paramaters/CombinedConstructedDirectories"
experimentName = "Papers/Paper_2/Extension/Experiment_18_Membership_Rhythmn.py"

configLocation = f"{configDirectory}/{configName}"

os.system(f"python {experimentName} {configLocation}")