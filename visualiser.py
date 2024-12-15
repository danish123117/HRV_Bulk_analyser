import os
import matplotlib.pyplot as plt

def save_plot(ibi_series, corrected_ibi, save_path, loss):
    # Validate inputs
    if not ibi_series or not corrected_ibi:
        print("Error: Input series are empty or invalid.")
    if loss is None:
        print("Error: Loss value is None.")
    if not os.path.isdir(os.path.dirname(save_path)):
        print(f"Error: Directory does not exist for save path: {save_path}")
    
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(ibi_series, label="Original IBI Series", marker='o', markersize=4, linewidth=.3)
    plt.plot(corrected_ibi, label="Corrected IBI Series", marker='x', markersize=4, linewidth=.3)
    plt.legend()
    plt.xlabel("Time Index")
    plt.ylabel("IBI")
    plt.title("Artifact Correction in IBI Time Series")
    plt.grid()

    # Add text box
    bbox_props = dict(boxstyle="round", facecolor="white", edgecolor="black", alpha=0.8)
    plt.text(
        0.9,  # x
        0.95,  # y
        f"Artefacts : {loss}%",  # text content
        transform=plt.gca().transAxes,  # use Axes coordinates
        fontsize=10,  # font size
        verticalalignment='top',  # align text vertically
        horizontalalignment='center',  # align text horizontally
        bbox=bbox_props  # style the text box
    )

    # Save the plot
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved successfully at {save_path}")
    except Exception as e:
        print(f"Error saving plot: {e}")
    finally:
        plt.close()  # Close the plot to free memory
