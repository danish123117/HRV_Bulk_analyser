from functions import timeDomainFeatures
import pandas as pd
import numpy as np 
import os
import time
from artefact import correct_ibi_artifacts_thresh
from benchekron import* 
start_time = time.time()

with open("Monday w1 -p.txt", 'r') as file:
    lst_raw = [float(line.strip()) for line in file]
lst = correct_ibi_artifacts_thresh(lst_raw, threshold="Very Strong",unit="s",med_kernel_size=5 ,Benchekroun = False)
lst2=merge_ibi_series_algorithm(lst_raw,unit = "s")
lst3 = correct_ibi_artifacts_thresh(lst_raw, threshold="Strong",unit="s",med_kernel_size=5 ,Benchekroun = True)
results =[]

tdf0 = timeDomainFeatures(lst_raw,t="s")
type1 = {"Type":0}
identity_tdf= {**type1 , **tdf0}
results.append(identity_tdf)
tdf = timeDomainFeatures(lst,t="s")
type1 = {"Type":1}
identity_tdf= {**type1 , **tdf}
results.append(identity_tdf)
tdf2 = timeDomainFeatures(lst2,t="s")
type1 = {"Type":2}
identity_tdf= {**type1 , **tdf2}
results.append(identity_tdf)
tdf3 = timeDomainFeatures(lst3,t="s")
type1 = {"Type":3}
identity_tdf= {**type1 , **tdf2}
results.append(identity_tdf)

testcase = pd.DataFrame(results)
testcase.to_excel("test2.xlsx", index=False)

# commentry on results https://doi.org/10.52082/jssm.2022.260 
# strong impact of artefacts on RMSSD

