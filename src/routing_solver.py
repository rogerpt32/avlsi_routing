import sys
import os
import subprocess

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

if sys.version_info[0] < 3 or (sys.version_info[0]==3 and sys.version_info[1]<7):
        raise Exception("Must use Python 3.7 or above (dataclass package)")

from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Pair:
    p1: Point
    p2: Point

# Input:
# n m (x and y max sizes)
# p (total number of pairs)
# x1 y1 x1' y1'
# ...
# xn yn xn' yn'

def usage():
    print("Usage:")
    print("\tpython3.7 routing_solver.py [pb_file] [-not_opt]")
    print("Input:")
    print("\tn m (x and y max sizes)")
    print("\tp (total number of pairs)")
    print("\tx1 y1 x1' y1'")
    print("\t...")
    print("\txn yn xn' yn'")
    exit(-1)

def check_points(points, n, m):
    for i in range(len(points)):
        p=points[i]
        if(p.p1.x>=n or p.p2.x>=n or p.p1.y>=m or p.p2.y>=m 
                or p.p1.x<0 or p.p2.x<0 or p.p1.y<0 or p.p2.y<0):
            raise Exception("Point out of bounds")
        if(p.p1.x==p.p2.x and p.p1.y==p.p2.y):
            raise Exception("Points overlapped")
        for j in range(i+1, len(points)):
            pj=points[j]
            if((p.p1.x==pj.p1.x and p.p1.y==pj.p1.y) or
                (p.p1.x==pj.p2.x and p.p1.y==pj.p2.y) or
                (p.p2.x==pj.p1.x and p.p2.y==pj.p1.y) or 
                (p.p2.x==pj.p2.x and p.p2.y==pj.p2.y)):
                raise Exception("Points overlapped")

def get_adjacent(point, n, m, pair_id): # returns the cells next to it
    adj=[]
    if point.x > 0:
        adj.append(point.x+(n*point.y)+(n*m*pair_id))
    if point.y > 0:
        adj.append(point.x+(n*(point.y-1))+(n*m*pair_id)+1)
    if point.x < n-1:
        adj.append(point.x+(n*point.y)+(n*m*pair_id)+2)
    if point.y < m-1:
        adj.append(point.x+(n*(point.y+1))+(n*m*pair_id)+1)
    return adj

def constraint_point_adjacents(adj, pb_file):
    for cell in adj:
        pb_file.write("+1 x%d "%cell)
    pb_file.write(" = 1;\n")

def constraint_cell_adjacents(adj, cell, pb_file):
    for adj_cell in adj:
        pb_file.write("-1 x%d "%adj_cell)
    pb_file.write(" +3 ~x%d >= -2;\n"%cell)
    for adj_cell in adj:
        pb_file.write("+1 x%d "%adj_cell)
    pb_file.write(" +3 ~x%d >= 2;\n"%cell)

def generate_pseudo_boolean(points, n, m, p, pb_filename, c_max):
    pb_file = open(pb_filename,"w")
    total_vars = m*n*p
    total_constraints = p*4 + (n*m-2*p)*p*2 + n*m + 1
    if c_max==n*m: total_constraints-=1
    pb_file.write("* #variable= %d #constraint= %d\n"%(total_vars,total_constraints))
    pb_file.write("min: ")
    for i in range(1,n*m*p+1):
        pb_file.write(" +1 x%d"%i)
    pb_file.write(";\n")
    visited=[]
    for i in range(p):
        pos1=points[i].p1.x+(n*points[i].p1.y)+(n*m*i)+1
        pos2=points[i].p2.x+(n*points[i].p2.y)+(n*m*i)+1
        visited.append(pos1-(n*m*i)-1)
        visited.append(pos2-(n*m*i)-1)
        adj1=get_adjacent(points[i].p1,n,m,i)
        adj2=get_adjacent(points[i].p2,n,m,i)
        pb_file.write("1 x%d >= 1;\n"%pos1)
        pb_file.write("1 x%d >= 1;\n"%pos2)
        constraint_point_adjacents(adj1,pb_file)
        constraint_point_adjacents(adj2,pb_file)
    
    for x in range(n):
        for y in range(m):
            if not x+n*y in visited:
                for i in range(p):
                   adj=get_adjacent(Point(x,y),n,m,i)
                   constraint_cell_adjacents(adj,x+n*y+n*m*i+1,pb_file)
            for i in range(p):
                pb_file.write(" -1 x%d"%(x+n*y+n*m*i+1))
            pb_file.write(" >= -1;\n")

    if c_max!=n*m:
        for i in range(1,n*m*p+1):
            pb_file.write(" -1 x%d"%i)
        pb_file.write(">= -%d;\n"%c_max)

    pb_file.close()

def show_solution(sol_out,n,m):
    lines = sol_out.split('\n')
    i=0
    while(not lines[i].startswith("v ")):
        i+=1
    sol_line = lines[i].split()
    sol = np.zeros((n,m),dtype=int)
    if sol_line[0]!="v": 
        print("unexpected error")
        exit(-1)
    for j in range(1,len(sol_line)):
        if sol_line[j].startswith("x"):
            group = 1 + ((j-1)//(n*m))
            position = (j-1)-(n*m*group)
            y=position//n
            x=position-n*y
            sol[x][y]=group
    print(sol)
    fig, ax = plt.subplots()
    ax.matshow(sol, cmap=plt.cm.gist_ncar_r,vmin=0)
    for i in range(n):
        for j in range(m):
            c = sol[i,j]
            ax.text(j, i, str(c), va='center', ha='center')
    plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../results/optimal_solution.png'))
    plt.show()

def show_not_optimal_solution(sol_out,n,m,points):
    lines = sol_out.split('\n')
    i=0
    while(not lines[i].startswith("v ")):
        i+=1
    sol_line = lines[i].split()
    sol = np.zeros((n,m),dtype=int)
    if sol_line[0]!="v": 
        print("unexpected error")
        exit(-1)
    for j in range(1,len(sol_line)):
        if sol_line[j].startswith("x"):
            group = 1 + ((j-1)//(n*m))
            position = (j-1)-(n*m*group)
            y=position//n
            x=position-n*y
            sol[x][y]=group
    sol_filtered = np.zeros((n,m),dtype=int)
    for i in range(len(points)):
        p2=points[i].p2
        sol_filtered[points[i].p1.x][points[i].p1.y]=i+1
        current = points[i].p1
        walking=True
        while current.x!=p2.x or current.y!=p2.y:
            if current.x+1<n and sol[current.x+1][current.y]==i+1 and sol_filtered[current.x+1][current.y]==0:
                sol_filtered[current.x+1][current.y]=i+1
                current.x+=1
            elif current.y+1<m and sol[current.x][current.y+1]==i+1 and sol_filtered[current.x][current.y+1]==0:
                sol_filtered[current.x][current.y+1]=i+1
                current.y+=1
            elif current.x-1>=0 and sol[current.x-1][current.y]==i+1 and sol_filtered[current.x-1][current.y]==0:
                sol_filtered[current.x-1][current.y]=i+1
                current.x-=1
            elif current.y-1>=0 and sol[current.x][current.y-1]==i+1 and sol_filtered[current.x][current.y-1]==0:
                sol_filtered[current.x][current.y-1]=i+1
                current.y-=1
            else:
                raise Exception("Unexpected Error")

    print(sol)
    fig, ax = plt.subplots()
    ax.matshow(sol_filtered, cmap=plt.cm.gist_ncar_r,vmin=0)
    for i in range(n):
        for j in range(m):
            c = sol_filtered[i,j]
            ax.text(j, i, str(c), va='center', ha='center')
    plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../results/not_optimal_solution.png'))
    plt.show()
    exit(0)

def check_solution(solution,n,m,p):
    lines = solution.split('\n')
    i=0
    while(not lines[i].startswith("s ")):
        i+=1
    sat_line = lines[i]
    if 'UNSAT' in sat_line:
        # print('UNSAT')
        return False
    else:
        # print('SAT')
        return True

def min_distance(points):
    minimal = 0
    for p in points:
        minimal += abs(p.p1.x-p.p2.x)+abs(p.p1.y-p.p2.y)+1
    return minimal

def main(argc, argv):

    ## Reading arguments
    pb_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../data/pb/out.opb")
    optimize=True
    if argc==2 :
        if argv[1]=="-not-opt" or argv[1]=="-no":
            optimize=False
        else:
            pb_filename = argv[1]
    elif argc==3:
        if argv[1]=="-not-opt" or argv[1]=="-no":
            optimize=False
            pb_filename=argv[2]
        elif argv[2]=="-not-opt" or argv[2]=="-no":
            optimize=False
            pb_filename=argv[1]
        else: usage()
    elif argc>3:
        usage()
    
    ## Reading Input
    line=input("Insert n and m\n").split()
    if len(line)!=2:
        usage()
    n,m=int(line[0]),int(line[1])
    p=int(input("Insert number of pairs\n"))
    points=[]
    print("Insert all pairs (one pair per line)")
    for _ in range(p):
        line=input()
        line=line.split()
        if len(line)!=4:
            usage()
        p1=Point(int(line[0]),int(line[1]))
        p2=Point(int(line[2]),int(line[3]))
        points.append(Pair(p1,p2))
    check_points(points,n,m)
    print("Input successfully read")
    # print(points)

    ## Generating Pseudo Boolean
    print("Generating Pseudo Boolean...",end="",flush=True)
    generate_pseudo_boolean(points, n, m, p, pb_filename, n*m)
    print("done")

    ## Solving with pbsolver
    print("Solving problem with pbsolver...",end="",flush=True)
    solver = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../BasicPBSolver/pbsolver")
    proc = subprocess.run([solver,pb_filename,'model'], stdout=subprocess.PIPE, encoding='ascii')
    print("done")
    if not check_solution(proc.stdout,n,m,p): 
        print("Unfeasible problem")
    else:
        print("Solution found!")
        if not optimize:
            show_not_optimal_solution(proc.stdout,n,m,points)
        else:
            print("Optimizing...")
            right_sol = proc.stdout
            left = min_distance(points)
            right = n*m
            print("Trying cost=%d..."%left,end='',flush=True)
            generate_pseudo_boolean(points, n, m, p, pb_filename, left)
            solver = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../BasicPBSolver/pbsolver")
            proc = subprocess.run([solver,pb_filename,'model'], stdout=subprocess.PIPE, encoding='ascii')
            if check_solution(proc.stdout,n,m,p):
                print("SAT")
                print("Found Optimal Solution:")
                show_solution(proc.stdout,n,m)
            else:
                print("UNSAT")
                while(left+1<right):
                    c_max=(left+right)//2
                    if(c_max==left): c_max+=1
                    print("Trying cost=%d..."%c_max,end='',flush=True)
                    generate_pseudo_boolean(points, n, m, p, pb_filename, c_max)
                    solver = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../BasicPBSolver/pbsolver")
                    proc = subprocess.run([solver,pb_filename,'model'], stdout=subprocess.PIPE, encoding='ascii')
                    if check_solution(proc.stdout,n,m,p):
                        print("SAT")
                        right=c_max
                        right_sol=proc.stdout
                    else:
                        print("UNSAT")
                        left=c_max
            print("Found Optimal Solution:")
            show_solution(right_sol,n,m)

  
if __name__== "__main__":
    main(len(sys.argv), sys.argv)