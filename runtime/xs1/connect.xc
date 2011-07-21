#include "globals.h"
#include "util.h"
#include "connect.h"

#define NONE (-1)
#define MASTER 1
#define SLAVE  0

bool dequeueMasterReq(conn_req &r, int conn_id);
bool dequeueSlaveReq(conn_req &r, int conn_id);
void queueMasterReq(int conn_id, unsigned thread_cri, unsigned chan_cri);
void queueSlaveReq(unsigned tid, int conn_id, 
    unsigned thread_cri, unsigned chan_cri);

/*
 * Complete one side of a connection by sending the CRI of the other party.
 */
inline
COMPLETE_PARTY(unsigned c, unsigned cri, unsigned v)
{ SETD     (conn_master, cri);
  OUT      (conn_master, v);
  OUTCT_END(conn_master);
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

  // If the slave end is local and this is executing on thread 0 then we want
  // to queue or complete the connection without causing an interrupt.
  if (tid == 0 && dest == GET_GLOBAL_CORE_ID(c))
  { DISABLE_INTERRUPTS();
    conn_req sReq;
    if (!dequeueSlaveReq(sReq, connId))
    { queueMasterReq(connId, t, c);
      // Wait for slave request
      ENABLE_INTERRUPTS();
    }
    else
    { COMPLETE(conn_master, sReq.theadCRI, c);
      SETD(c, sReq.chanCRI);
      ENABLE_INTERRUPTS();
      return c;
    }
  }
  // Otherwise, we proceede over a channel connection
  else
  { unsigned destCRI = GEN_CHAN_RI(dest, 1);
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

  // If executing on thread 0, we don't want to interrupt ourselves.
  if (tid == 0)
  { DISABLE_INTERRUPTS();
    conn_req mReq;
    if (!dequeueMasterReq(mReq, connId))
    { queueSlaveReq(connId, t, c);
      ENABLE_INTERRUPTS();
    }
    else
    { COMPLETE(conn_master, mReq.threadCRI, c);
      SETD(c, mReq.chanCRI);
      ENABLE_INTERRUPTS();
      return c;
    }
  }
  else
  { unsigned destCRI = (c & 0xFFFF0000) | (GEN_CHAN_RI(0, 1) & 0xFFFF);
    SETD(t, destCRI);
    OUT(t, t);
    OUT(t, SLAVE);
    OUT(t, tid);
    OUT(t, c);
    OUT(t, connId);
    OUTCT_END(t);
  }
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
      queueMasterReq(connId, mThreadCRI, mChanCRI);
    else
    { COMPLETE(threadCRI, sReq.chanCRI);
      COMPLETE(sReq.threadCRI, mChanCRI);
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
      queueSlaveReq(tid, connId, sThreadCRI, sChanCRI);
    else
    { COMPLETE(mReq.threadCRI, sChanCRI);
      COMPLETE(threadCRI, mReq.chanCRI);
    }
  }
}

/*
 * Initialise the conn_buffer and conn_local arrays.
 */
#pragma unsafe arrays
void initConnections()
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
    conn_buffer[i].conn_id = NONE;
  for (int i=0; i<MAX_THREADS; i++)
    conn_locals[i].conn_id = NONE;
}

/*
 * Dequeue a master connection request matching the channel id.
 */
bool dequeueMasterReq(conn_req &r, int conn_id)
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
  { if (conn_buffer[i].conn_id == conn_id)
    { conn_buffer[i].conn_id = NONE;
      r.thread_cri = conn_buffer[i].thread_cri;
      r.chan_cri = conn_buffer[i].chan_cri;
      return true;
    }
  }
  return false;
}

/*
 * Dequeue a slave connection request.
 */
bool dequeueSlaveReq(conn_req &r, int conn_id)
{ for (int i=0; i<MAX_THREADS; i++)
  { if (conn_locals[i].conn_id == conn_id)
    { conn_locals[i].conn_id = NONE;
      r.thread_cri = conn_locals[i].thread_cri;
      r.chan_cri = conn_locals[i].chan_cri;
      return true;
    }
  }
  return false;
}

/*
 * Queue a master connection request: insert it in the next available slot in
 * the buffer.
 */
void queueMasterReq(int conn_id, unsigned thread_cri, unsigned chan_cri)
{ int i = 0;
  char b = 0;
  while (i<CONN_BUFFER_SIZE && !b)
  { if (conn_buffer[i].conn_id == NONE)
    { conn_buffer[i].conn_id = conn_id;
      conn_buffer[i].thread_cri = thread_cri;
      conn_buffer[i].chan_cri = chan_cri;
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
void queueSlaveReq(unsigned tid, int conn_id, 
    unsigned thread_cri, unsigned chan_cri)
{ conn_locals[tid].conn_id = conn_id;
  conn_locals[tid].thread_cri = thread_cri;
  conn_locals[tid].chan_cri = chan_cri;
}

