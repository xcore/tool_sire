#include "globals.h"
#include "util.h"
#include "connect.h"

#define EMPTY (-1)
#define NONE  (0)
#define MASTER 1
#define SLAVE  0

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
  OUT(c, c);
  OUTCT_END(c);
  CHKCT_END(c);
  OUTS(c, MASTER);
  OUTS(c, chanid);
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
  OUT(c, c);
  OUTCT_END(c);
  CHKCT_END(c);
  OUTS(c, SLAVE);
  OUTS(c, GET_THREAD_ID());
  OUTS(c, chanid);
  destcri = INS(c);
  SETD(c, destcri);
  return c;
}

/*
 * Queue a master connection request: insert it in the next available slot in
 * the buffer.
 */
void queueMasterReq(int chanid, unsigned destcri)
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
unsigned dequeueMasterReq(int chanid)
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
void queueSlaveReq(unsigned tid, int chanid, unsigned destcri)
{ conn_locals[tid].chanid = chanid;
  conn_locals[tid].destcri = destcri;
}

/*
 * Dequeue a slave connection request.
 */
unsigned dequeueSlaveReq(int chanid)
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
void serveMasterConnReq(unsigned m_destcri)
{ int chanid = INS(conn_master);

  // Check if slave side is complete, if not, queue it, otherwise complete.
  unsigned s_destcri = dequeueSlaveReq(chanid);
  if (s_destcri == NONE) 
    queueMasterReq(chanid, m_destcri);
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
void serveSlaveConnReq(unsigned s_destcri)
{ unsigned tid    = INS(conn_master);
  int      chanid = INS(conn_master);

  // Check if master side is complete, if not, queue it, otherwise complete. 
  unsigned m_destcri = dequeueMasterReq(chanid);
  if (m_destcri == NONE)
    queueSlaveReq(tid, chanid, s_destcri);
  else
  { SETD(conn_master, m_destcri);
    OUTS(conn_master, s_destcri);
    SETD(conn_master, s_destcri);
    OUTS(conn_master, m_destcri);
  }
}

void connHandler()
{ unsigned srcCri = IN(conn_master);
  CHKCT_END(conn_master);
  SETD(conn_master, srcCri);
  OUTCT_END(conn_master);
 
  //asm("waiteu");

  if(INS(conn_master) == MASTER)
    serveMasterConnReq(srcCri);
  else
    serveSlaveConnReq(srcCri);
}

