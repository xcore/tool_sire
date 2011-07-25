#include "util.h"
#include "globals.h"
#include "connect.h"

#define NONE (-1)
#define MASTER 1
#define SLAVE  0

bool dequeueMasterReq(conn_req &r, int connId);
bool dequeueSlaveReq(conn_req &r, int connId);
void queueMasterReq(int connId, unsigned threadCRI, unsigned chanCRI);
void queueSlaveReq(unsigned tid, int connId, 
    unsigned threadCRI, unsigned chanCRI);

/*
 * Complete one side of a connection by sending the CRI of the other party.
 */
inline
COMPLETE(unsigned c, unsigned cri, unsigned v)
{ SETD(c, cri);
  OUT(c, v);
  OUTCT_END(c);
}

/*
 * Master connection protocol:
 *  0. Get a new channel c and construct target CRI (conn_master).
 *  1. Output channel id on (separate) thread channel t.
 *  2. Output CRI on t.
 *  3. Input slave CRI on t.
 *  4. Set local channel destination of c and return it.
 */
unsigned _connectmaster(int connId, unsigned dest)
{ int tid = GET_THREAD_ID();
  unsigned t = thread_chans[tid];
  unsigned c = GETR_CHANEND();
  unsigned destCRI = GEN_CHAN_RI(dest, 1);
  SETD(t, destCRI);
  OUT(t, t);
  OUT(t, MASTER);
  OUT(t, c);
  OUT(t, connId);
  OUTCT_END(t);
  destCRI = IN(t);
  CHKCT_END(t);
  SETD(c, destCRI);
  return c;
}

/*
 * Slave connection protocol:
 *  0. Get a new channel c and construct (local) dest CRI (conn_master).
 *  1. Output thread id on (separate) thread channel t.
 *  2. Output channel id on t.
 *  3. Output CRI on t.
 *  4. Input master CRI on t.
 *  5. Set local channel destination of c and return it.
 */
unsigned _connectslave(int connId)
{ int tid = GET_THREAD_ID();
  unsigned t = thread_chans[tid];
  unsigned c = GETR_CHANEND();
  unsigned destCRI = (c & 0xFFFF0000) | (GEN_CHAN_RI(0, 1) & 0xFFFF);
  SETD(t, destCRI);
  OUT(t, t);
  OUT(t, SLAVE);
  OUT(t, tid);
  OUT(t, c);
  OUT(t, connId);
  OUTCT_END(t);
  destCRI = IN(t);
  CHKCT_END(t);
  SETD(c, destCRI);
  return c;
}

/*
 * Handle an incoming master or slave connection request.
 *
 * Thread 0 serve master connection request.
 *  1. Receive channel id
 *  2. Receive master CRI
 *  [queue or complete]
 *
 * Thread 0 serve slave connection request.
 *  1. Receive slave thread id
 *  2. Receive channel id
 *  3. Receive slave CRI
 *  [queue or complete]
 */
void connHandler()
{ unsigned threadCRI = IN(conn_master);
  SETD(conn_master, threadCRI);

  // Master request
  if(IN(conn_master) == MASTER)
  { unsigned mChanCRI = IN(conn_master);
    int connId = IN(conn_master);
    conn_req sReq;
    CHKCT_END(conn_master);
    if (!dequeueSlaveReq(sReq, connId))
      queueMasterReq(connId, threadCRI, mChanCRI);
    else
    { COMPLETE(threadCRI, sReq.threadCRI, sReq.chanCRI);
      COMPLETE(sReq.threadCRI, threadCRI, mChanCRI);
    }
  }
  // Slave request
  else
  { unsigned tid = IN(conn_master);
    unsigned sChanCRI = IN(conn_master);
    int connId = IN(conn_master);
    conn_req mReq;
    CHKCT_END(conn_master);
    if (!dequeueMasterReq(mReq, connId))
      queueSlaveReq(tid, connId, threadCRI, sChanCRI);
    else
    { COMPLETE(mReq.threadCRI, threadCRI, sChanCRI);
      COMPLETE(threadCRI, mReq.threadCRI, mReq.chanCRI);
    }
  }
}

/*
 * Initialise the conn_buffer and conn_local arrays.
 */
#pragma unsafe arrays
void initConnections()
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
    conn_buffer[i].connId = NONE;
  for (int i=0; i<MAX_THREADS; i++)
    conn_locals[i].connId = NONE;
}

/*
 * Dequeue a master connection request matching the channel id.
 */
bool dequeueMasterReq(conn_req &r, int connId)
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
  { if (conn_buffer[i].connId == connId)
    { conn_buffer[i].connId = NONE;
      r.threadCRI = conn_buffer[i].threadCRI;
      r.chanCRI = conn_buffer[i].chanCRI;
      return true;
    }
  }
  return false;
}

/*
 * Dequeue a slave connection request.
 */
bool dequeueSlaveReq(conn_req &r, int connId)
{ for (int i=0; i<MAX_THREADS; i++)
  { if (conn_locals[i].connId == connId)
    { conn_locals[i].connId = NONE;
      r.threadCRI = conn_locals[i].threadCRI;
      r.chanCRI = conn_locals[i].chanCRI;
      return true;
    }
  }
  return false;
}

/*
 * Queue a master connection request: insert it in the next available slot in
 * the buffer.
 */
void queueMasterReq(int connId, unsigned threadCRI, unsigned chanCRI)
{ int i = 0;
  char b = 0;
  while (i<CONN_BUFFER_SIZE && !b)
  { if (conn_buffer[i].connId == NONE)
    { conn_buffer[i].connId = connId;
      conn_buffer[i].threadCRI = threadCRI;
      conn_buffer[i].chanCRI = chanCRI;
      b = 1;
    }
    i = i + 1;
  }
  // Check if the buffer is full
  //TODO: if (!b) assert 0;
}

/*
 * Queue a slave connection request: insert it in the slot given by the thread
 * id.
 */
void queueSlaveReq(unsigned tid, int connId, 
    unsigned threadCRI, unsigned chanCRI)
{ conn_locals[tid].connId = connId;
  conn_locals[tid].threadCRI = threadCRI;
  conn_locals[tid].chanCRI = chanCRI;
}

