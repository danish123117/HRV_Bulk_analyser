import numpy as np
from scipy.signal import medfilt
from scipy.interpolate import CubicSpline
import numpy as np
import matplotlib.pyplot as plt

# https://doi.org/10.3390/s22051984
def compute_dynamic_threshold(ibi_series, current_idx, window_size=10):
    """
    Compute E10 dynamically as a sliding window over the RR intervals.

    Parameters:
        ibi_series (list): List of RR intervals.
        current_idx : index of the current RR interval
        window_size (int): Size of the sliding window.

    Returns:
        float: Dynamic threshold E10 for the current window (capped at 0.4).
    """
    start_idx = current_idx -10
    end_idx = min(start_idx + window_size, len(ibi_series))
    window = ibi_series[start_idx-1:end_idx]
    differences = np.abs(np.diff(window) / window[:-1])  # Compute relative differences
    E10 = np.mean(differences)
    return min(E10, 0.4)  # Enforce the condition E10 ≤ 0.4

def compute_Rr(RRj, RRj2):
    return abs((RRj2 - RRj) / RRj)

def compute_Rl(RRj, RRj2):
    return abs((RRj - RRj2) / RRj2)

def merge_ibi_series_algorithm(ibi_series, window_size=10, unit ="ms"):
    """
    Implements the HRV filtering procedure with dynamic E10 calculation.

    Parameters:
        ibi_series (list): List of RR intervals (in seconds).
        window_size (int): Size of the window for dynamic threshold calculation.

    Returns:
        list: Updated RR intervals after merging.
    """
    # convert from milliseconds to seconds.
    if unit not in ["s", "ms"]:
        raise ValueError("Unit must be either 's' or 'ms'.")
    conversion_factor = 1.0 if unit == "s" else 1000.0
    ibi_series = np.array(ibi_series) / conversion_factor
    ibi_series = ibi_series[ibi_series>0]
    valid = np.ones(len(ibi_series), dtype=bool)  # Mask to track valid entries

    i = 11
    while i < len(ibi_series) - 1:
        if ibi_series[i] < 0.3:
            # Compute dynamic threshold E10
            E10 = compute_dynamic_threshold(ibi_series, i, window_size)

            # Compute right error (Equation 6,7 refer doi )

            RRr = ibi_series[i] + ibi_series[i + 1]
            ERr = compute_Rr(RRr, ibi_series[i + 1])
            ERl = compute_Rl(RRr, ibi_series[i-1])
            Etotr = ERr+ERl
            if RRr < 1.3 and ERr <= E10 and ERl <= E10:
                # Right merge
                ibi_series[i + 1] = RRr
                valid[i] = False
            else:
                RRl = ibi_series[i] + ibi_series[i - 1]
                ELr = compute_Rr(RRl, ibi_series[i + 1])
                ELl = compute_Rl(RRl, ibi_series[i-1])
                Etotl = ELr+ELl
                if RRl < 1.3 and ELr <= E10 and ELl<= E10:
                    # Left merge
                    ibi_series[i] = RRl
                    valid[i-1] = False
                elif RRr > 1.3 and RRl > 1.3:
                    # Delete both
                    valid[i:i + 2] = False
                elif RRr < 1.3 and RRl > 1.3:
                    # Right merge
                    ibi_series[i + 1] = RRr
                    valid[i] = False
                elif RRr > 1.3 and RRl < 1.3:
                    # Left merge
                    ibi_series[i - 1] = RRl
                    valid[i] = False
                elif (
                    RRr < 1.3
                    and RRl < 1.3
                    and Etotl > E10
                    and Etotr > E10
                ):
                    # Keep the one with the smaller error
                    if Etotl < Etotr:
                        ibi_series[i - 1] = RRl
                        valid[i] = False
                    else:
                        ibi_series[i + 1] = RRr
                        valid[i] = False
        i += 1

    # Filter valid intervals
    ibi_series=ibi_series[valid]
    ibi_series = ibi_series[ibi_series<=1.3]
    ibi_series = ibi_series*conversion_factor
    return ibi_series

if __name__ == "__main__":
    with open("Monday w1 -p.txt", 'r') as file:
        ibi_series = [float(line.strip()) for line in file]

    corrected_ibi = merge_ibi_series_algorithm(ibi_series,unit = "s")

    plt.figure(figsize=(10, 5))
    plt.plot(ibi_series, label="Original IBI Series", marker='o',markersize = 4, linewidth=.3)
    plt.plot(corrected_ibi, label="Corrected IBI Series", marker='x',markersize = 4, linewidth=.3)
    plt.legend()
    plt.xlabel("Time Index")
    plt.ylabel("IBI (s)")
    #plt.yscale('log')
    plt.title("Artifact Correction in IBI Time Series")
    plt.grid()
    plt.show()