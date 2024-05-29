import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def simplePlot(x_values, y_values, x_label, y_label, plot_title=None, x_lim_min=None, x_lim_max=None, scatter=None):
    # Create a line plot
    
    if scatter == None:
        plt.figure(figsize=(15, 10))
        plt.plot(x_values, y_values, marker='x', label='Power Samples', zorder=2)
    else:
        plt.figure(figsize=(15, 10))
        print(f"X values: {len(x_values)}")
        print(f"Y values: {len(y_values)}")
        plt.scatter(x_values, y_values, label='Power Samples', s=40, marker='x', zorder=2)

    if x_lim_min != None:
        plt.axvline(x=x_lim_min, color='r', linestyle='--')  # Red dashed line at x_lim_min
    if x_lim_max != None:
        plt.axvline(x=x_lim_max, color='g', linestyle='--')   # Green dotted line at x=4

    # Add labels and title
    plt.xlabel(x_label, fontsize=24)
    plt.ylabel(y_label, fontsize=24)
    plt.title(plot_title, fontsize=32)

    # plt.grid(True, zorder=1)
    plt.grid(True, linestyle='-', linewidth=0.5, color='gray', alpha=0.5, which='both')

    plt.xticks(x_values, fontsize=20)
    plt.yticks(fontsize=20)

    # Add a legend
    plt.legend(fontsize=20)

    # Show the plot
    plt.show(block=True)

def psuRawPlot(psu_logs, y_min=None, y_max=None, x_lim_min=None, x_lim_max=None, title=None):
    time = []
    power = []

    for index, psu_log in enumerate(psu_logs):
        
        if psu_log.time_psu > y_min and psu_log.time_psu < y_max:
            power.append(psu_log.volts)
            time.append(psu_log.time_psu)

        #if (psu_log.starttime > 10):
        #    break
    
    if title == None:
        simplePlot(time, power, "Time [s]", "Power [W]", "Power Consumption Synchronized with Transmissions", x_lim_min, x_lim_max)
    else:
        simplePlot(time, power, "Time [s]", "Power [W]", title, x_lim_min, x_lim_max)

def simplePlotTwoYValues(x_values, y_values1, y_values2, x_axis_label, y_axis_label, y_label1, y_label2, plot_title):
    # Create a line plot
    # plt.scatter(x_values, y_values, label='Power Samples', s=0.5, zorder=2)
    plt.plot(x_values, y_values2, label=y_label2, color='red', zorder=2)
    plt.plot(x_values, y_values1, label=y_label1, color='blue', zorder=2)

    # Add labels and title
    plt.xlabel(x_axis_label, fontsize=16)
    plt.ylabel(y_axis_label, fontsize=16)
    plt.title(plot_title, fontsize=16)
    plt.grid(True, zorder=1)

    plt.xticks(x_values, fontsize=16)
    plt.yticks(fontsize=20)

    # Add a legend
    plt.legend(fontsize=10)

    # Show the plot
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show(block=True)

def psuRawPlotVA(psu_logs, y_min=None, y_max=None, title=None):
    time = []
    power = []
    amperes = []

    for index, psu_log in enumerate(psu_logs):
        
        if psu_log.time_psu > y_min and psu_log.time_psu < y_max:
            power.append(psu_log.volts)
            amperes.append(psu_log.amperes)
            time.append(psu_log.time_psu)

        #if (psu_log.starttime > 10):
        #    break
    
    if title == None:
        simplePlotTwoYValues(time, power, amperes, "Time [s]", "Voltage [V]", "Amperes [A]", "Voltage and Amperes")
    else:
        simplePlotTwoYValues(time, power, amperes, "Time [s]", "Voltage [V]", "Amperes [A]", title)

def plotWithLines(x_values, y_values, x_label, y_label, plot_title, y_max, lines_array=None, y_min_lim=None, y_max_lim=None):
    # Create a line plot
    colors = ['Green', 'Blue', 'Red', 'Black', 'Yellow', 'Purple', 'Brown']
    colors_legend = ['PRACH', 'Registration Complete', 'PUSCH', 'PDCCH', 'PDSCH', 'PUCCH']

    plt.plot(x_values, y_values, label='Power Samples', zorder=2)
    # if y_min_lim != None and y_max_lim != None:
        # plt.axhline(y=y_min_lim, color='red', linestyle='--', linewidth=1)  # Horizontal line at y-value
        # plt.axhline(y=y_max_lim, color='red', linestyle='--', linewidth=1)  # Horizontal line at y-value

    if lines_array != None:
        for i, lines in enumerate(lines_array):
            plt.plot([], [], color=colors[i], label=colors_legend[i])
            for line in lines:
                if line < y_max:
                    plt.axvline(x=line, color=colors[i], linestyle='--', linewidth=1)  # Red dashed line at x_lim_min
                    plt.axvline(x=line+0.00049, color=colors[i], linewidth=0.5)  # Red dashed line at x_lim_min
                    
                    rect = patches.Rectangle((line, 0), 0.0005, max(y_values), linewidth=0.5, edgecolor=colors[i], facecolor=colors[i], alpha=0.3)
                    # Add the rectangle patch to the plot
                    plt.gca().add_patch(rect)

    # Add labels and title
    plt.xlabel(x_label, fontsize=16)
    plt.ylabel(y_label, fontsize=16)
    plt.title(plot_title, fontsize=16)
    plt.grid(True, zorder=1)

    plt.yticks(fontsize=20)
    plt.xticks(fontsize=20)

    # Add a legend
    plt.legend(fontsize=10)

    # Show the plot
    plt.get_current_fig_manager().window.state('zoomed')
    plt.show(block=True)

def psuRawPlotWithLinesArray(psu_logs, y_min=None, y_max=None, lines_array=None, y_min_lim=None, y_max_lim=None):
    time = []
    power = []

    for index, psu_log in enumerate(psu_logs):
        
        if psu_log.time_psu > y_min and psu_log.time_psu < y_max:
            power.append(psu_log.power)
            time.append(psu_log.time_psu)

        #if (psu_log.starttime > 10):
        #    break
    
    plotWithLines(time, power, "Time [s]", "Power [W]", "Power Consumption Synchronized with Transmissions", y_max, lines_array, y_min_lim, y_max_lim)

def plotConfidenceInterval(x_values, y_values, lower_ci, upper_ci):
    x_values = np.array(x_values)
    y_values = np.array(y_values)
    lower_ci = np.array(lower_ci)
    upper_ci = np.array(upper_ci)
    # Plot data points
    plt.scatter(x_values, y_values, color='blue', label='Data (Mean)')

    # Plot error bars for confidence intervals
    plt.errorbar(x_values, y_values, yerr=[y_values - lower_ci, upper_ci - y_values], fmt='.', color='red', label='95% CI')

    # Add labels and legend
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Plot with Confidence Intervals')
    plt.legend()

    plt.yticks(fontsize=20)
    plt.xticks(fontsize=20)

    # Show plot
    plt.grid(True)
    plt.show()

def evaluatePmax(mcs=None, tx_rx=None):
    
    # Read the CSV file into a DataFrame
    if tx_rx == 'tx':
        df = pd.read_csv(os.path.join('DeepLearning', 'tx', 'prev', 'data' + '.csv'))
    elif tx_rx == 'rx':
        df = pd.read_csv(os.path.join('DeepLearning', 'rx', 'data' + '.csv'))

    # Specify the desired 'MCS' and 'MIMO' values
    if mcs == None:
        mcs_value = 10
    else:
        mcs_value = mcs
    mimo_value = 2

    # Filter the DataFrame based on the specified 'MCS' and 'MIMO' values
    filtered_df = df[(df['mcs'] == mcs_value) & (df['mimo'] == mimo_value)]

    # Group by 'pmax' and calculate the average label for each group
    average_labels = filtered_df.groupby('pmax')['label'].mean()

    mimo_value = 1
    # Filter the DataFrame based on the specified 'MCS' and 'MIMO' values
    filtered_df2 = df[(df['mcs'] == mcs_value) & (df['mimo'] == mimo_value)]

    # Group by 'pmax' and calculate the average label for each group
    average_labels2 = filtered_df2.groupby('pmax')['label'].mean()

    p_max = [7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5]

    simplePlot(p_max[::-1], average_labels, "Power Transmission [dBm]", "Power Consumption [W]", "Power Consumption based on Power Transmission for MIMO 2x2", scatter=1)
    simplePlotTwoYValues(p_max[::-1], average_labels, average_labels2, 'Transmission Power [dBm]', "Power Consumption [W]", 'MIMO 2x2', 'SISO', 'Power consumption based on Transmission Power for SISO and MIMO 2x2')
    simplePlot(p_max[::-1], average_labels2, "Power Transmission [dBm]", "Power Consumption [W]", "Power Consumption based on Power Transmission for SISO", scatter=1)

def evaluateMcs(tx_rx=None):
        # Read the CSV file into a DataFrame
    if tx_rx == 'tx':
        df = pd.read_csv(os.path.join('DeepLearning', 'tx', 'prev', 'data' + '.csv'))
    elif tx_rx == 'rx':
        df = pd.read_csv(os.path.join('DeepLearning', 'rx', 'prev', 'data' + '.csv'))

    # Specify the desired 'MCS' and 'MIMO' values
    mimo_value = 1
    pmax = 10
    
    mcs_index1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    mcs_index2 = [29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]

    # Filter the DataFrame based on the specified 'MCS' and 'MIMO' values
    if tx_rx == 'tx':
        filtered_mcs64 = df[(df['pmax'] == pmax) & (df['mimo'] == mimo_value) & (df['mcs'].isin(mcs_index1))]
        filtered_mcs256 = df[(df['pmax'] == pmax) & (df['mimo'] == mimo_value) & (df['mcs'].isin(mcs_index2))]
    elif tx_rx == 'rx':
        filtered_mcs64 = df[(df['mimo'] == mimo_value) & (df['mcs'].isin(mcs_index1))]
        filtered_mcs256 = df[(df['mimo'] == mimo_value) & (df['mcs'].isin(mcs_index2))]

    # Group by 'pmax' and calculate the average label for each group
    average_labels_filtered_mcs64 = filtered_mcs64.groupby('mcs')['label'].mean()
    average_labels_filtered_mcs256 = filtered_mcs256.groupby('mcs')['label'].mean()

    simplePlot(mcs_index1, average_labels_filtered_mcs64, "MCS Index", "Power Consumption [W]", "Power Consumption based on MCS Index for table 64QAM", scatter=1)
    simplePlot(mcs_index1[:10], average_labels_filtered_mcs256, "MCS Index", "Power Consumption [W]", "Power Consumption based on MCS Index for table 256QAM", scatter=1)