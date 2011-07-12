#include "globals.h"
#include "util.h"
#include "connect.h"

/*
 * Master connection.
 */
unsigned _connectmaster(int chanid, unsigned dest)
{ unsigned c = GETR_CHANEND();
  unsigned destcri = GEN_CHAN_RI(dest, 1);
  SETD(c, destcri);
  OUTS(c, c);
  OUTS(c, chanid);
  destcri = INS(c);
  SETD(c, destcri);
  return c;
}

/*
 * Slave connection.
 */
unsigned _connectslave(int chanid)
{ unsigned c = GETR_CHANEND();
  unsigned destcri = (c & 0xFFFF0000) | (GEN_CHAN_RI(0, 1) & 0xFFFF);
  SETD(c, destcri);
  OUTS(c, GET_THREAD_ID());
  OUTS(c, c);
  OUTS(c, chanid);
  destcri = INS(c);
  SETD(c, destcri);
  return c;
}

void queue_req(int chanid, unsigned destcri)
{
}

/*
 * Thread 0 serve master connection request.
 */
void serve_master_conn_req()
{ int chanid = INS(conn_master);
  unsigned destcri = INS(conn_master);
  queue_req(chanid, destcri);

  // Check if slave side is complete
}

/*
 * Thread 0 serve slave connection request.
 */
void serve_slave_conn_req()
{ unsigned tid = INS(conn_master);
  int chanid = INS(conn_master);
  unsigned destcri = INS(conn_master);
  conn_locals[tid].chanid = chanid;
  conn_locals[tid].destcri = destcri;

  // Check if master side is complete
}

