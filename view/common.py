import matplotlib.pyplot as plt

def simplePlot(x_values, y_values, x_label, y_label, plot_title, x_lim_min=None, x_lim_max=None):
    # Create a line plot
    # plt.scatter(x_values, y_values, label='Power Samples', s=0.5, zorder=2)
    plt.plot(x_values, y_values, label='Power Samples', zorder=2)

    if x_lim_min != None:
        plt.axvline(x=x_lim_min, color='r', linestyle='--')  # Red dashed line at x_lim_min
    if x_lim_max != None:
        plt.axvline(x=x_lim_max, color='g', linestyle='--')   # Green dotted line at x=4

    # Add labels and title
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(plot_title)
    plt.grid(True, zorder=1)

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()
    plt.show(block=True)

def psuRawPlot(psu_logs, y_min=None, y_max=None, x_lim_min=None, x_lim_max=None):
    time = []
    power = []

    for index, psu_log in enumerate(psu_logs):
        
        if psu_log.time_psu > y_min and psu_log.time_psu < y_max:
            power.append(psu_log.power)
            time.append(psu_log.time_psu)

        #if (psu_log.starttime > 10):
        #    break
    
    simplePlot(time, power, "Time [s]", "Power [W]", "Raw PSU Plot", x_lim_min, x_lim_max)
