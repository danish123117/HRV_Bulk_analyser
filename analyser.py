from functions import*
import pandas as pd
import numpy as np 
import os
import time
from artefact import*
from benchekron import merge_ibi_series_algorithm
from visualiser import save_plot 
from pyhrv import frequency_domain as fd
import neurokit as nk
start_time = time.time()

folder_path_outer = "D:/POLIMI WORK/OneDrive - Politecnico di Milano/STUDY/ECG data analysis/RR_pieces/"
folder_save_img = "D:/POLIMI WORK/OneDrive - Politecnico di Milano/STUDY/ECG data analysis/Compiled analysis/PSD plots - welch method/"
# Get list of file names in the folder
sub_folder_names = os.listdir(folder_path_outer)
fdf_template = {
                "VLF(%)": np.nan,
                "LF(%)": np.nan,
                "HF(%)": np.nan,
                "VLF(ms^2)": np.nan,
                "LF(ms^2)": np.nan,
                "HF(ms^2)": np.nan,
                "LF/HF": np.nan,
                "TotalPower": np.nan,
            }
for folder in sub_folder_names: 
    files_list = os.listdir(folder_path_outer+folder)
    os.makedirs(folder_save_img+folder, exist_ok=True)
    results = []
    for files in files_list: 
        print(folder_path_outer+folder+"/"+files)
        with open(folder_path_outer+folder+"/"+files, 'r') as file:
            lst_raw = [float(line.strip()) for line in file]
        lst_raw =remove_zeros(lst_raw)
        print(len(lst_raw))
        #lst_raw=trim_data_baseline(lst_raw=lst_raw,t=60, unit = "ms" ) # for baseline estimation we take only last 60 seconds of the rest period
        # apply benchekron filter 
        lst1 = merge_ibi_series_algorithm(lst_raw,unit = "ms")
        # apply kubios like filter
        lst = correct_ibi_artifacts_thresh(lst1 , threshold="Strong",unit="ms",med_kernel_size=5 )
        len_raw= len(lst_raw)
        len_clean=len(lst)
        art_percent = (100*(len_raw-len_clean)/len_raw) if len_raw>0  else 0
        
        #save_plot(lst_raw,lst,folder_save_img+folder+"/"+files.rstrip(".txt")+".png",art_percent)
        
        length=np.sum(lst_raw)
        tdf = timeDomainFeatures(lst,t="ms")
        try:
            #test2 = fd.lomb_psd(lst, rpeaks=None, fbands=None, nfft=2**8, ma_size=None, show=False, show_param=False, legend=False)
            #test3 = fd.ar_psd(nn=None, rpeaks=None, fbands=None, nfft=2**12, order=16, show=False, show_param=False, legend=False)
            test = fd.welch_psd(lst, show=False, show_param=True, legend=False)
            plt.savefig(folder_save_img+folder+"/"+files.rstrip(".txt")+".png")  # Save as a PNG file
            plt.close()
            fdf = {
                    "VLF(%)": test["fft_rel"][0],
                    "LF(%)": test["fft_rel"][1],
                    "HF(%)": test["fft_rel"][2],
                    "VLF(ms^2)": test["fft_abs"][0],
                    "LF(ms^2)": test["fft_abs"][1],
                    "HF(ms^2)": test["fft_abs"][2],
                    "LF/HF": test["fft_ratio"],
                    "TotalPower": test["fft_total"],
                }

        except Exception as e:
            print(f"An error occurred: {e}")
            fdf = fdf_template
        # apparently the welch_psd fucntion of pyhrv generates the images despite of using show=False so we get an error
        # "Failed to allocate Bitmap" since it uses matplitlib for plotting, calling plt.close("all") closes the generated plot and hence clears the memory
        plt.close('all')  
        identify= {"Participant": folder, "File":files.rstrip(".txt")}
        total_time = {"Length(ms)":length, "Count RRi": len_raw }
        identity_tdf= {**identify, **tdf,**fdf, ** total_time}
        results.append(identity_tdf)
    participant_n_unsorted = pd.DataFrame(results)
    #participant_n_unsorted['File'] = pd.to_numeric(participant_n_unsorted['File'])
    participant_n_sorted=participant_n_unsorted.sort_values(by='File')
    participant_n_sorted.to_excel(folder+".xlsx", index=False)

end_time = time.time()

runtime = end_time - start_time
print(f"Runtime: {runtime:.4f} seconds")