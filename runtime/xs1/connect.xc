#include "globals.h"
#include "util.h"
#include "connect.h"

/*
 * Master connection.
 */
unsigned _connectmaster(unsigned dest, int chanid)
{ unsigned c = GETR_CHANEND();
  unsigned destcri = GEN_CHAN_RI_0(dest);
  SETD(c, destcri);
  OUTS(c, c);
  OUTS(c, chanid);
  destcri = INS(c);
  FREER(c);
  return destcri;
}

/*
 * Slave connection.
 */
unsigned _connectslave(int chanid)
{ int threadid = GET_THREAD_ID();
  unsigned c = GETR_CHANEND();
  unsigned destcri; 
  conn_ids[threadid] = chanid;
  conn_slaves[threadid] = c;
  destcri = INS(c);
  SETD(c, destcri);
  OUTS(c, c);
  FREER(c);
  return destcri;
}

/*
 * Thread 0 connection request reception.
 */
void _receiveconnection()
{ unsigned destcri = INS(conn_master);
  unsigned chanid = INS(conn_master);

}

