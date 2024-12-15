import numpy as np
from scipy.signal import medfilt
from scipy.interpolate import CubicSpline
import numpy as np
import matplotlib.pyplot as plt
import neurokit2 as nk



def correct_ibi_artifacts_thresh(ibi_series, threshold="None", heart_rate=60, unit="ms", med_kernel_size =5):
    


    return corrected_ibi.tolist()

# Example usage
if __name__ == "__main__":

    with open("Monday w1 -p.txt", 'r') as file:
        ibi_series = [float(line.strip()) for line in file]
    # Correct artifacts
    corrected_ibi = correct_ibi_artifacts_thresh(ibi_series)

    # Plot original and corrected IBI series
    plt.figure(figsize=(10, 5))
    plt.plot(ibi_series, label="Original IBI Series", marker='o')
    plt.plot(corrected_ibi, label="Corrected IBI Series", marker='x')
    plt.legend()
    plt.xlabel("Time Index")
    plt.ylabel("IBI (s)")
    plt.yscale('log')
    plt.title("Artifact Correction in IBI Time Series")
    plt.grid()
    plt.show()