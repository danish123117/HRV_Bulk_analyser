import numpy as np
from scipy.signal import medfilt
from scipy.interpolate import CubicSpline
import numpy as np
import matplotlib.pyplot as plt
from functions import rawHR


def remove_zeros(ibi_series):
    ibi_series = np.array(ibi_series)
    ibi_series= ibi_series[ibi_series>0]
    return ibi_series.tolist()
    

def correct_ibi_artifacts_thresh(ibi_series, threshold="None", unit="ms", med_kernel_size =5):
    """
    Correct artifacts in an IBI time series based on a threshold method.
    
    Parameters:
        ibi_series (list): Array of inter-beat intervals (IBIs) in seconds.
        threshold (str): Threshold level ("None", "Very Low", "Low", "Medium", "Strong", "Very Strong", or float for custom value).
        custom_threshold (float): Custom threshold in seconds.
        heart_rate (float): Mean heart rate in beats per minute (adjusts thresholds accordingly).
    
    Returns:
        list: Corrected IBI time series.
    """
    # Threshold values (adjusted based on a 60 bpm heart rate)
    if threshold == "None":
        return ibi_series
    
    heart_rate=rawHR(ibi_series,unit)
    threshold_map = {
        "Very Low": 0.45,
        "Low": 0.35,
        "Medium": 0.25,
        "Strong": 0.15,
        "Very Strong": 0.05
    } #https://www.kubios.com/downloads/Kubios_HRV_Users_Guide.pdf 
    if unit not in ["s", "ms"]:
        raise ValueError("Unit must be either 's' or 'ms'.")
    
    conversion_factor = 1.0 if unit == "s" else 1000.0
    ibi_series = np.array(ibi_series) / conversion_factor
    ibi_series = ibi_series[ibi_series>0]
    if isinstance(threshold, str):
        threshold = threshold_map.get(threshold, 100)  # Default 100 >> expected value therefore 
    else:
        # If threshold is already a numeric value, keep it
        pass

    # Adjust threshold based on heart rate https://www.kubios.com/downloads/Kubios_HRV_Users_Guide.pdf 
    threshold *= (60 / heart_rate)

    # Compute the local average using median filtering
    ibi_series = np.array(ibi_series)
    local_avg = medfilt(ibi_series, kernel_size=med_kernel_size)  # Adjust kernel size as needed

    # Identify artifacts
    diff = np.abs(ibi_series - local_avg)
    artifacts = diff > threshold

    # Replace artifacts using cubic spline interpolation
    x = np.arange(len(ibi_series))
    x_valid = x[~artifacts]
    y_valid = ibi_series[~artifacts]

    # Ensure there are enough valid points for interpolation
    if len(x_valid) < 2:
        print("Not enough valid points to perform interpolation.")
        return ibi_series.tolist()

    spline = CubicSpline(x_valid, y_valid)
    corrected_ibi = ibi_series.copy()
    corrected_ibi[artifacts] = spline(x[artifacts])    
    corrected_ibi *= conversion_factor
    return corrected_ibi.tolist()

# Example usage
if __name__ == "__main__":

    with open("Monday w1 -p.txt", 'r') as file:
        ibi_series = [float(line.strip()) for line in file]
    # Correct artifacts
    corrected_ibi = correct_ibi_artifacts_thresh(ibi_series, threshold="Strong",unit="s",med_kernel_size=5 )

    # Plot original and corrected IBI series
    plt.figure(figsize=(10, 5))
    plt.plot(ibi_series, label="Original IBI Series", marker='o', markersize=4, linewidth=.3)
    plt.plot(corrected_ibi, label="Corrected IBI Series\n test", marker='x', markersize=4, linewidth=.3)
    plt.legend()
    plt.xlabel("Time Index")
    plt.ylabel("IBI (s)")
    # plt.yscale('log')
    plt.title("Artifact Correction in IBI Time Series")
    plt.grid()
    bbox_props = dict(boxstyle="round", facecolor="white", edgecolor="black", alpha=0.8)
    plt.text(
    .9,  # x-coordinate (adjust based on your legend's position)
    .95,  # y-coordinate (adjust to position the text just under the legend)
    "Corrections : 3.5%",  # text content
    transform=plt.gca().transAxes,  # use Axes coordinates
    fontsize=10,  # font size
    verticalalignment='top',  # align text vertically
    horizontalalignment='center',  # align text horizontally
    bbox=bbox_props  # style the text box
    )
    # Save the graph
    plt.savefig("ibi_correction_plot.png", dpi=300, bbox_inches='tight')
    #plt.show()
    '''percentage corrections, length before and after, graphs, alert on length which is shorter than 11, malik et al
    # Static name for methods params
    MALIK_RULE = "malik"
    KARLSSON_RULE = "karlsson"
    KAMATH_RULE = "kamath"
    ACAR_RULE = "acar"
    CUSTOM_RULE = "custom"
    benchekron 
    
    '''