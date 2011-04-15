#include <stdlib.h>
#include <stdio.h>
#include "mpi.h"

#include "slave.h"
#include "program.h"

int main(int argc, char* argv[])
{ 
  int rank, size;

  rc = MPI_Init(&argc, &argv);
  if (rc != MPI_SUCCESS) 
  { printf("Error starting MPI program. Terminating.\n");
    MPI_Abort(MPI_COMM_WORLD, rc);
  } 
  
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);
  
  MPI_Barrier(MPI_COMM_WORLD);
  printf("%d of %d\n", rank, size);

  // Master
  if (rank == 0)
  { _main();
  }

  // Slave
  else
  { slave(rank);
  } 
  
  MPI_Barrier(MPI_COMM_WORLD);
  MPI_Finalize();

  return 0;
}

