#include <stdlib.h>
#include <stdio.h>
#include "mpi.h"
#include "program.h"

int main(int argc, char* argv[]) { 

    int rank, size;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    printf("Hello, world, I am %d of %d\n", rank, size);

    _main();
    
    MPI_Barrier(MPI_COMM_WORLD);
    MPI_Finalize();

    return 0;
}

