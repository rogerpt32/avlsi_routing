import sys
import os

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
    print("\tpython3 pb_generator.py [outfile]")
    print("Input:")
    print("\tn m (x and y max sizes)")
    print("\tp (total number of pairs)")
    print("\tx1 y1 x1' y1'")
    print("\t...")
    print("\txn yn xn' yn'")
    exit(-1)

def check_points(points, n, m):
    for p in points:
        if(p.p1.x>=n or p.p2.x>=n or p.p1.y>=m or p.p2.y>=m 
                or p.p1.x<0 or p.p2.x<0 or p.p1.y<0 or p.p2.y<0):
            raise Exception("Point out of bounds")

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

def constraint_point_adjacents(adj, outfile):
    for cell in adj:
        outfile.write("+1 x%d "%cell)
    outfile.write(" = 1;\n")

def constraint_cell_adjacents(adj, cell, outfile):
    for adj_cell in adj:
        outfile.write("-1 x%d "%adj_cell)
    outfile.write(" +3 ~x%d >= -2;\n"%cell)
    for adj_cell in adj:
        outfile.write("+1 x%d "%adj_cell)
    outfile.write(" +3 ~x%d >= 2;\n"%cell)

def main(argc, argv):
    if(argc==1):
        filename = "../data/pb/out.opb"
    elif(argc==2):
        filename = argv[1]
    else:
        usage()
    line=input().split()
    if len(line)!=2:
        usage()
    n,m=int(line[0]),int(line[1])
    p=int(input())
    points=[]
    for _ in range(p):
        line=input()
        line=line.split()
        if len(line)!=4:
            usage()
        p1=Point(int(line[0]),int(line[1]))
        p2=Point(int(line[2]),int(line[3]))
        points.append(Pair(p1,p2))
    check_points(points,n,m)
    # print(points)
    # outfile = open(os.path.join(path,filename),"w")
    outfile = open(filename,"w")
    total_vars = m*n*p
    total_constraints = m*n*p*3
    outfile.write("* #variable= %d #constraint= %d\n"%(total_vars,total_constraints))
    outfile.write("min: ")
    for i in range(1,n*m*p+1):
        outfile.write(" +1 x%d"%i)
    outfile.write(";\n")
    visited=[]
    for i in range(len(points)):
        pos1=points[i].p1.x+(n*points[i].p1.y)+(n*m*i)+1
        pos2=points[i].p2.x+(n*points[i].p2.y)+(n*m*i)+1
        visited.append(pos1-(n*m*i)-1)
        visited.append(pos2-(n*m*i)-1)
        adj1=get_adjacent(points[i].p1,n,m,i)
        adj2=get_adjacent(points[i].p2,n,m,i)
        outfile.write("1 x%d >= 1;\n"%pos1)
        outfile.write("1 x%d >= 1;\n"%pos2)
        constraint_point_adjacents(adj1,outfile)
        constraint_point_adjacents(adj2,outfile)
    
    for x in range(n):
        for y in range(m):
            for i in range(p):
                if not x+n*y in visited:
                   adj=get_adjacent(Point(x,y),n,m,i)
                   constraint_cell_adjacents(adj,x+n*y+n*m*i+1,outfile)

    for x in range(n):
        for y in range(m):
            for i in range(p):
                outfile.write(" -1 x%d"%(x+n*y+n*m*i+1))
            outfile.write(" >= -1;\n")
  
if __name__== "__main__":
    main(len(sys.argv), sys.argv)