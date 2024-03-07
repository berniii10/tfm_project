import matplotlib.pyplot as plt

def simplePlot(x_values, y_values, x_label, y_label, plot_title):
    # Create a line plot
    plt.plot(x_values, y_values, label='Sample Line')

    # Add labels and title
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(plot_title)

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()
    plt.show(block=True)

def psuRawPlot(psu_logs):
    volts = []
    amperes = []
    time = []

    for index, psu_log in enumerate(psu_logs):

        if index % 5 == 0:
            continue
        
        amperes.append(psu_log.amperes)
        volts.append(psu_log.volts)
        time.append(psu_log.starttime)

        #if (psu_log.starttime > 10):
        #    break
    
    simplePlot(time, amperes, "Time", "Amperes", "Raw PSU Plot")
