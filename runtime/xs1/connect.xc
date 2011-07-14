#include "globals.h"
#include "util.h"
#include "connect.h"

#define EMPTY (-1)
#define NONE  (0)

/*
 * Master connection protocol:
 *  1. Output channel id
 *  2. Output CRI
 *  3. Input slave CRI
 *  4. Set local channel destination and return channel.
 */
unsigned _connectmaster(int chanid, unsigned dest)
{ unsigned c = GETR_CHANEND();
  unsigned destcri = GEN_CHAN_RI(dest, 1);
  SETD(c, destcri);
  OUTS(c, chanid);
  OUTS(c, c);
  destcri = INS(c);
  SETD(c, destcri);
  return c;
}

/*
 * Slave connection protocol:
 *  1. Output thread id
 *  2. Output channel id
 *  3. Output CRI
 *  4. Input master CRI
 *  5. Set local channel destination and return channel.
 */
unsigned _connectslave(int chanid)
{ unsigned c = GETR_CHANEND();
  unsigned destcri = (c & 0xFFFF0000) | (GEN_CHAN_RI(0, 1) & 0xFFFF);
  SETD(c, destcri);
  OUTS(c, GET_THREAD_ID());
  OUTS(c, chanid);
  OUTS(c, c);
  destcri = INS(c);
  SETD(c, destcri);
  return c;
}

/*
 * Queue a master connection request: insert it in the next available slot in
 * the buffer.
 */
void queue_master_req(int chanid, unsigned destcri)
{ int i = 0;
  char b = 0;
  while (i<CONN_BUFFER_SIZE && !b)
  { if (conn_buffer[i].chanid == EMPTY)
    { conn_buffer[i].chanid = chanid;
      conn_buffer[i].destcri = destcri;
      b = 1;
    }
    i = i + 1;
  }
  // Check if the buffer is full
  //TODO: if (!b) assert 0;
}

/*
 * Dequeue a master connection request matching the channel id.
 */
unsigned dequeue_master_req(int chanid)
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
  { if (conn_buffer[i].chanid == chanid)
    { conn_buffer[i].chanid = EMPTY;
      return conn_buffer[i].destcri;
    }
  }
  return NONE;
}

/*
 * Queue a slave connection request: insert it in the slot given by the thread
 * id.
 */
void queue_slave_req(unsigned tid, int chanid, unsigned destcri)
{ conn_locals[tid].chanid = chanid;
  conn_locals[tid].destcri = destcri;
}

/*
 * Dequeue a slave connection request.
 */
unsigned dequeue_slave_req(int chanid)
{ for (int i=0; i<MAX_THREADS; i++)
  { if (conn_locals[i].chanid == chanid)
    { conn_locals[i].chanid = EMPTY;
      return conn_locals[i].destcri;
    }
  }
  return NONE;
}

/*
 * Thread 0 serve master connection request.
 *  1. Receive channel id
 *  2. Receive master CRI
 *  [queue or complete]
 */
void serve_master_conn_req()
{ int      chanid    = INS(conn_master);
  unsigned m_destcri = INS(conn_master);

  // Check if slave side is complete, if not, queue it, otherwise complete.
  unsigned s_destcri = dequeue_slave_req(chanid);
  if (s_destcri == NONE) 
    queue_master_req(chanid, m_destcri);
  else
  { SETD(conn_master, m_destcri);
    OUTS(conn_master, s_destcri);
    SETD(conn_master, s_destcri);
    OUTS(conn_master, m_destcri);
  }
}

/*
 * Thread 0 serve slave connection request.
 *  1. Receive slave thread id
 *  2. Receive channel id
 *  3. Receive slave CRI
 *  [queue or complete]
 */
void serve_slave_conn_req()
{ unsigned tid       = INS(conn_master);
  int      chanid    = INS(conn_master);
  unsigned s_destcri = INS(conn_master);

  // Check if master side is complete, if not, queue it, otherwise complete. 
  unsigned m_destcri = dequeue_master_req(chanid);
  if (m_destcri == NONE)
    queue_slave_req(tid, chanid, s_destcri);
  else
  { SETD(conn_master, m_destcri);
    OUTS(conn_master, s_destcri);
    SETD(conn_master, s_destcri);
    OUTS(conn_master, m_destcri);
  }
}

