import matplotlib.pyplot as plt
import matplotlib.patches as patches

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
            power.append(psu_log.amperes)
            time.append(psu_log.time_psu)

        #if (psu_log.starttime > 10):
        #    break
    
    simplePlot(time, power, "Time [s]", "Power [W]", "Raw PSU Plot", x_lim_min, x_lim_max)


def plotWithLines(x_values, y_values, x_label, y_label, plot_title, y_max, lines_array=None):
    # Create a line plot
    colors = ['Green', 'Blue', 'Red', 'Black', 'Yellow', 'Purple', 'Brown']
    colors_legend = ['PRACH', 'Registration Complete', 'PUSCH', 'PDCCH', 'PDSCH', 'PUCCH']

    plt.plot(x_values, y_values, label='Power Samples', zorder=2)

    if lines_array != None:
        for i, lines in enumerate(lines_array):
            plt.plot([], [], color=colors[i], label=colors_legend[i])
            for line in lines:
                if line < y_max:
                    plt.axvline(x=line, color=colors[i], linestyle='--', linewidth=1)  # Red dashed line at x_lim_min
                    # # plt.axvline(x=line+0.00049, color=colors[i], linewidth=0.5)  # Red dashed line at x_lim_min
                    
                    rect = patches.Rectangle((line, 0), 0.0005, max(y_values), linewidth=0.5, edgecolor=colors[i], facecolor=colors[i], alpha=0.3)
                    # Add the rectangle patch to the plot
                    plt.gca().add_patch(rect)

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

def psuRawPlotWithLinesArray(psu_logs, y_min=None, y_max=None, lines_array=None):
    time = []
    power = []

    for index, psu_log in enumerate(psu_logs):
        
        if psu_log.time_psu > y_min and psu_log.time_psu < y_max:
            power.append(psu_log.power)
            time.append(psu_log.time_psu)

        #if (psu_log.starttime > 10):
        #    break
    
    plotWithLines(time, power, "Time [s]", "Power [W]", "Raw PSU Plot", y_max, lines_array)
