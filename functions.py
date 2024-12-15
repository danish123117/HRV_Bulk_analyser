import numpy as np
from scipy import signal
#from scipy.ndimage import label
#from scipy.stats import zscore
from scipy.interpolate import interp1d
from pyhrv import frequency_domain

def timeDomainFeatures(rr_list,t):
    '''
    Takes a list or rr intervals as input and outputs
    a dictionary of time domain features
    '''
    if t=="s":
      d=1000
    else:
      d=1
    hrv_tdf ={}
    rr_list_np_unfilter = np.array(rr_list)*d # this results in order of magnitude difference in processing times
    
    rr_list_np = rr_list_np_unfilter[rr_list_np_unfilter>0]
    meanRR = np.mean(rr_list_np) #1
    hrv_tdf['meanRR'] = meanRR
#    meanHR = 60000/meanRR #2
#    hrv_tdf['meanHR']= meanHR
    SDNN = np.std(rr_list_np, ddof=1)#3 # N-1 in denominator so ddof =1, we treat the readings as a sample
    hrv_tdf['SDNN'] = SDNN
    diffs = np.diff(rr_list_np)
    abs_diffs= np.abs(diffs)
 #   SDSD = np.std(diffs, ddof=1)
 #   hrv_tdf['SDSD'] = SDSD
    NN = len(diffs)
    RMSSD = np.sqrt(np.mean(diffs**2))#4
    hrv_tdf['RMSSD']= RMSSD
 #   NN50 = np.sum(abs_diffs >50)#5
#    hrv_tdf['NN50']= NN50
#    NN20 = np.sum(abs_diffs >20)#6
#    pNN50 =(NN50*100)/(NN) #7
#    hrv_tdf['pNN50'] = pNN50
#    pNN20 = (NN20*100)/(NN)#8
#    hrv_tdf['pNN20']= pNN20

    return hrv_tdf

def rawHR(rr_list,t):
    if t=="s":
      d=1000
    else:
      d=1
    rr_list_np_unfilter = np.array(rr_list)*d # this results in order of magnitude difference in processing times
    rr_list_np = rr_list_np_unfilter[rr_list_np_unfilter>0]
    meanRR = np.mean(rr_list_np) #1
    meanHR = 60000/meanRR #2  
    return meanHR

def trim_data_baseline(lst_raw,t=60, unit = "ms" ):
    if unit=="ms":
        d=1000
    else:
        d=1
    
    lst_raw.reverse()
    last_60 = []
    i=0
    while sum(last_60)<=t*d:
      last_60.append(lst_raw[i])
      i+=1
    last_60.reverse()
    return last_60
      
def frequency_domain_features(rr_list,fs=4,detrend = False, nperseg = 256, overlap = 0.5, f_bands=[[0.0003,0.04],[0.04,0.15],[0.15,0.4]] ):
   
   '''
   Inputs : 
   rr_list --> list of rr intervals 
   t --> unit of the rr intervals  could be either 's' or 'ms'
   
   '''
   rr_mean= np.mean(rr_list)
   if rr_mean > 100:
      d=1000
   else:
      d=1
  
   hrv_fdf={}
   # 
   x = np.cumsum(rr_list) / d
   rr_list = np.array(rr_list)*(1000/d)
   f = interp1d(x, rr_list, kind='cubic')

   fs = fs
   steps = 1 / fs

  # now we can sample from interpolation function
   xx = np.arange(1,np.max(x), steps)
   rr_interpolated = f(xx)
   fxx, pxx = signal.welch(x=rr_interpolated, fs=fs,nperseg=nperseg, noverlap= (nperseg//(1/overlap)),detrend=detrend ,window='hann')
#welch(x, fs=1.0, window='hann', nperseg=None, noverlap=None, nfft=None, detrend='constant', return_onesided=True, scaling='density', axis=-1, average='mean')
   cond_vlf = (fxx >= f_bands[0][0]) & (fxx < f_bands[0][1])
   cond_lf = (fxx >= f_bands[1][0]) & (fxx < f_bands[1][1])
   cond_hf = (fxx >= f_bands[2][0]) & (fxx < f_bands[2][1])

  # calculate power in each band by integrating the spectral density 
   vlf = np.trapezoid(pxx[cond_vlf], fxx[cond_vlf])
   lf = np.trapezoid(pxx[cond_lf], fxx[cond_lf])
   hf = np.trapezoid(pxx[cond_hf], fxx[cond_hf])

  # sum these up to get total power
   total_power = vlf + lf + hf

  # find which frequency has the most power in each band
   peak_vlf = fxx[cond_vlf][np.argmax(pxx[cond_vlf])]
   peak_lf = fxx[cond_lf][np.argmax(pxx[cond_lf])]
   peak_hf = fxx[cond_hf][np.argmax(pxx[cond_hf])]

  # fraction of lf and hf
   lf_nu = 100 * lf / (lf + hf)
   hf_nu = 100 * hf / (lf + hf)
   hrv_fdf['Power VLF (ms2)'] = vlf
   hrv_fdf['Power LF (ms2)'] = lf
   hrv_fdf['Power HF (ms2)'] = hf   
   hrv_fdf['Power Total (ms2)'] = total_power

   hrv_fdf['LF/HF'] = (lf/hf)
   hrv_fdf['Peak VLF (Hz)'] = peak_vlf
   hrv_fdf['Peak LF (Hz)'] = peak_lf
   hrv_fdf['Peak HF (Hz)'] = peak_hf

   hrv_fdf['Fraction LF (nu)'] = lf_nu
   hrv_fdf['Fraction HF (nu)'] = hf_nu
   return hrv_fdf #, fxx, pxx

if __name__ == "__main__":
    with open("12.txt", 'r') as file:
        ibi_series = [float(line.strip()) for line in file]
    test1 = frequency_domain.welch_psd(nni=ibi_series,detrend=False, show=False)
    test = frequency_domain_features(ibi_series)
    print(test)