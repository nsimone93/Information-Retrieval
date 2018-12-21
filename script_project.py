import os
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import MultiComparison
import matplotlib as mpl
mpl.use('tkagg')
import matplotlib.pyplot as plt


class Measure:  #define the array with the measures of interest
    def __init__(self, topic, ap, rprec, p_10):
        self.topic = topic
        self.ap = ap
        self.rprec = rprec
        self.p_10 = p_10


class Structure: #define the structure that for each run stores the array of measures for each topic
    def __init__(self, filename, ntopic):
        self.ntopic = ntopic
        self.filename = filename
        self.measure = []


def create_file(path): #create an array with the path of the measurement files
    file = []
    file.append(path+"results/run/evaluation/TF_IDF.txt")
    file.append(path+"results/run/evaluation/BM25.txt")
    file.append(path+"results/run/evaluation/BM25_porter.txt")
    file.append(path+"results/run/evaluation/TF_IDF_not.txt")
    return file


def data(file): #initialize and memorize the structure with the measures inside
    structure = []
    for j in range(len(file)):
        structure.append(Structure(file[j], 50))
        f = open(file[j], "r").read().split("\n")
        k = 0
        for i in range(len(f)):
            line = f[i].split()
            if len(line) > 1:
                if line[0] == "map":
                    ap = line[2]
                    k = k+1
                elif line[0] == "Rprec":
                    rprec = line[2]
                    k = k+1
                elif line[0] == "P_10":
                    p_10 = line[2]
                    topic = line[1]
                    k = k+1
                if k == 3:
                    # setup the structure
                    structure[j].measure.append(Measure(topic, ap, rprec, p_10))
                    k = 0
    return structure


def create_ap_file(path, structure): #create the matrix with the Average Precision
    f = open(path+"results/Average_Precision.txt", "w")
    for i in range(structure[0].ntopic):
        for j in range(len(structure)):
            f.write(structure[j].measure[i].ap)
            if j != len(structure)-1:
                f.write(" ")
            else:
                f.write("\n")
    f.close()


def create_rprec_file(path, structure): #create the matrix with the Rprec
    f = open(path+"results/Rprec.txt", "w")
    for i in range(structure[0].ntopic):
        for j in range(len(structure)):
            f.write(structure[j].measure[i].rprec)
            if j != len(structure)-1:
                f.write(" ")
            else:
                f.write("\n")
    f.close()


def create_p_10_file(path, structure): #create the matrix with the P_10
    f = open(path+"results/P_10.txt", "w")
    for i in range(structure[0].ntopic):
        for j in range(len(structure)):
            f.write(structure[j].measure[i].p_10)
            if j != len(structure)-1:
                f.write(" ")
            else:
                f.write("\n")
    f.close()


def make_datagroup(structure, valutation): #create a data array and an array group that are used to calculate the Anova
    data = np.zeros(200)
    group = []
    for j in range(len(structure)):
        for i in range(structure[0].ntopic):
            if valutation == 'ap':
                data[j*structure[0].ntopic+i] = float(structure[j].measure[i].ap)
            elif valutation == 'p_10':
                data[j*structure[0].ntopic+i] = float(structure[j].measure[i].p_10)
            else:
                data[j*structure[0].ntopic+i] = float(structure[j].measure[i].rprec)
            if j == 0:
                group.append("TF_IDF")
            elif j == 1:
                group.append("BM25")
            elif j == 2:
                group.append("BM25_porter")
            else:
                group.append("TF_IDF_not")
    return data, group


def v_anova(structure, valutation): #create 4 arrays with Average Precision for each run
    v = []
    for j in range(len(structure)):
        data = []
        for i in range(structure[0].ntopic):
            if valutation == 'ap':
                data.append(structure[j].measure[i].ap)
            elif valutation == 'p_10':
                data.append(structure[j].measure[i].p_10)
            else:
                data.append(structure[j].measure[i].rprec)
        v.append(data)
    return v


def anova(structure, valutation): #calculate the Anova
    v = v_anova(structure, valutation)
    f, p = stats.f_oneway(v[0], v[1], v[2], v[3])
    return f, p


def print_anova(f, p):
    print('ANOVA One-way ')
    print('----------------------------------')
    print('F value:', f)
    print('P value:', p, '\n')


def tukey(structure, alpha, valutation): #Tukey calculation pairwise and multiple comparisons and finally print the plot
    if valutation == 'ap':
        data, group = make_datagroup(structure, valutation)
        mc = MultiComparison(data, group)
        result = mc.tukeyhsd(alpha)
        fig = result.plot_simultaneous()    # Plot group confidence intervals
        fig.set_figwidth(30)
        fig.set_figheight(20)
        axes = fig.gca()
        fig.suptitle('Tukey_HSD test', fontsize=40)
        axes.set_xlabel("Average Precision (AP)", fontsize=30)
        axes.tick_params(labelsize=30)
        fileplot = path+"results/run/plot/Tukey_HSD_test_ap.png"
        fig.savefig(fileplot, dpi=300)
        fw = open(path+"results/run/plot/tukey_HSD_ap.txt", "w")
        fw.write(str(result))
        print(result)
        fw.close()
    elif valutation == 'p_10':
        data, group = make_datagroup(structure, valutation)
        mc = MultiComparison(data, group)
        result = mc.tukeyhsd(alpha)
        fig = result.plot_simultaneous()    # Plot group confidence intervals
        fig.set_figwidth(30)
        fig.set_figheight(20)
        axes = fig.gca()
        fig.suptitle('Tukey_HSD test', fontsize=40)
        axes.set_xlabel("P(10)", fontsize=30)
        axes.tick_params(labelsize=30)
        fileplot = path+"results/run/plot/Tukey_HSD_test_p10.png"
        fig.savefig(fileplot, dpi=300)
        fw = open(path+"results/run/plot/tukey_HSD_p10.txt", "w")
        fw.write(str(result))
        print(result)
        fw.close()
    else:
        data, group = make_datagroup(structure, valutation)
        mc = MultiComparison(data, group)
        result = mc.tukeyhsd(alpha)
        fig = result.plot_simultaneous()    # Plot group confidence intervals
        fig.set_figwidth(30)
        fig.set_figheight(20)
        axes = fig.gca()
        fig.suptitle('Tukey_HSD test', fontsize=40)
        axes.set_xlabel("Rprec", fontsize=30)
        axes.tick_params(labelsize=30)
        fileplot = path+"results/run/plot/Tukey_HSD_test_rprec.png"
        fig.savefig(fileplot, dpi=300)
        fw = open(path+"results/run/plot/tukey_HSD_rprec.txt", "w")
        fw.write(str(result))
        print(result)
        fw.close()


def list_rprec(structure): #prepare an array with the Rprec for the plot
    rprec = []
    for j in range(len(structure)):
        data = []
        for i in range(structure[0].ntopic):
            data.append(float(structure[j].measure[i].rprec))
        rprec.append(data)
    return rprec


def list_p_10(structure): #prepare an array with the P_10 for the plot
    p_10 = []
    for j in range(len(structure)):
        data = []
        for i in range(structure[0].ntopic):
            data.append(float(structure[j].measure[i].p_10))
        p_10.append(data)
    return p_10


def list_topic(structure): #prepare an array with the topic for the plot
    topic = []
    for i in range(structure[0].ntopic):
        topic.append(structure[0].measure[i].topic)
    return topic


def list_run(): #prepare an array with the runs for the plot
    run = []
    run.append("TF_IDF")
    run.append("BM25")
    run.append("BM25_porter")
    run.append("TF_IDF_not")
    return run


def list_map(structure): #prepare an array with the MAP for the plot
    map = []
    for j in range(len(structure)):
        index = structure[j].ntopic
        map.append(float(structure[j].measure[index].ap))
    return map


def plot_rprec(topic, rprec): #plot Rprec
    files = os.listdir(path+"results/run/")
    if "plot" not in files:
        os.system("mkdir " + path + "results/run/plot")
    for i in range(len(rprec)):
        if i == 0:
            title = "TF_IDF with Stopword and Porter Stemmer"
            fileplot = path+"results/run/plot/Rprec_TF_IDF.png"
        elif i == 1:
            title = "BM25 with Stopword and Porter Stemmer"
            fileplot = path+"results/run/plot/Rprec_BM25.png"
        elif i == 2:
            title = "BM25 without Stopword with Porter Stemmer"
            fileplot = path+"results/run/plot/Rprec_BM25_porter.png"
        else:
            title = "TF_IDF without Stopword and Porter Stemmer"
            fileplot = path+"results/run/plot/Rprec_TF_IDF_not.png"
        plt.figure(figsize=(30, 20))
        plt.rcParams.update({'font.size': 22})
        plt.bar(topic, rprec[i], color='black')
        plt.xticks(rotation=90)
        plt.xlabel('Topic')
        plt.ylabel('Rprec')
        plt.suptitle(title, fontsize=40)
        plt.savefig(fileplot, dpi=300)
        plt.clf()


def plot_p_10(topic, p_10): #plot P_10
    files = os.listdir(path+"results/run/")
    if "plot" not in files:
        os.system("mkdir " + path + "results/run/plot")
    for i in range(len(rprec)):
        if i == 0:
            title = "TF_IDF with Stopword and Porter Stemmer"
            fileplot = path+"results/run/plot/P_10_TF_IDF.png"
        elif i == 1:
            title = "BM25 with Stopword and Porter Stemmer"
            fileplot = path+"results/run/plot/P_10_BM25.png"
        elif i == 2:
            title = "BM25 without Stopword with Porter Stemmer"
            fileplot = path+"results/run/plot/P_10_BM25_porter.png"
        else:
            title = "TF_IDF without Stopword and Porter Stemmer"
            fileplot = path+"results/run/plot/P_10_TF_IDF_not.png"
        plt.figure(figsize=(30, 20))
        plt.rcParams.update({'font.size': 22})
        plt.bar(topic, p_10[i], color='black')
        plt.xticks(rotation=90)
        plt.xlabel('Topic')
        plt.ylabel('P(10)')
        plt.suptitle(title, fontsize=40)
        plt.savefig(fileplot, dpi=300)
        plt.clf()


def plot_map(run, map): #plot MAP
    files = os.listdir(path+"results/run/")
    if "plot" not in files:
        os.system("mkdir " + path + "results/run/plot")
    title = "MAP for all runs"
    fileplot = path+"results/run/plot/MAP_all.png"
    plt.figure(figsize=(30, 20))
    plt.rcParams.update({'font.size': 22})
    plt.bar(run, map, 0.15, color='black')
    plt.xlabel('Run')
    plt.ylabel('MAP')
    plt.suptitle(title, fontsize=40)
    plt.savefig(fileplot, dpi=300)
    plt.clf()


path = "/Users/nsimone/Desktop/HW1/"
file = create_file(path)
structure = data(file)
create_ap_file(path, structure)
create_rprec_file(path, structure)
create_p_10_file(path, structure)
f, p = anova(structure, 'ap')
print_anova(f, p)
f, p = anova(structure, 'p_10')
print_anova(f, p)
f, p = anova(structure, 'rprec')
print_anova(f, p)
tukey(structure, 0.05, 'ap')
tukey(structure, 0.05, 'p_10')
tukey(structure, 0.05, 'rprec')
topic = list_topic(structure)
rprec = list_rprec(structure)
plot_rprec(topic, rprec)
p_10 = list_p_10(structure)
plot_p_10(topic, p_10)
run = list_run()
map = list_map(structure)
plot_map(run, map)