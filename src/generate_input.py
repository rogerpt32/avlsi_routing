import sys
import os
import subprocess

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors


def main(argc,argv):
    ## Reading arguments
    if(argc==1):
        out_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../results/inputs/input.png")
    elif(argc==2):
        out_filename = argv[1]

    ## Reading Input
    line=input("Insert n and m\n").split()
    n,m=int(line[0]),int(line[1])
    sol = np.zeros((n,m),dtype=int)
    p=int(input("Insert number of pairs\n"))
    points=[]
    print("Insert all pairs (one pair per line)")
    for i in range(p):
        line=input()
        line=line.split()
        sol[int(line[0])][int(line[1])]=i+1
        sol[int(line[2])][int(line[3])]=i+1

    print(sol)
    fig, ax = plt.subplots()
    ax.matshow(sol, cmap=plt.cm.gist_ncar_r,vmin=0)
    for i in range(n):
        for j in range(m):
            c = sol[i,j]
            ax.text(j, i, str(c), va='center', ha='center')
    plt.savefig(out_filename)
    plt.show()

if __name__== "__main__":
    main(len(sys.argv), sys.argv)