#include "pb2cnf.h" // encoding interface
#include "VectorClauseDatabase.h" // basic clause database
#include "PBParser.h" // parser for opb files
#include "SATSolverClauseDatabase.h"
// a clause database that adds all clauses
// directly to a SAT solver (minisat)

int main(int argc, char* argv[]){
    int m = 10;
    int n = 10;
    WeightedLit l1 = WeightedLit(1, 1); // literal, weight
    WeightedLit l2 = WeightedLit(2, 1);

}