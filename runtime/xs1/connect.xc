#include "globals.h"
#include "util.h"
#include "connect.h"

#define NONE (-1)
#define MASTER 1
#define SLAVE  0

/*
 * Master connection protocol:
 *  0. Get a new channel c and construct target CRI (conn_master).
 *  1. Output channel id on (separate) thread channel t.
 *  2. Output CRI on t.
 *  3. Input slave CRI on t.
 *  4. Set local channel destination of c and return it.
 */
unsigned _connectmaster(int conn_id, unsigned dest)
{ unsigned t = thread_chans[GET_THREAD_ID()];
  unsigned c = GETR_CHANEND();
  unsigned target_cri = GEN_CHAN_RI(dest, 1);
  SETD(t, target_cri);
  OUT(t, t);
  OUTCT_END(t);
  CHKCT_END(t);
  OUTS(t, MASTER);
  OUTS(t, c);
  OUTS(t, conn_id);
  target_cri = INS(t);
  SETD(c, target_cri);
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
unsigned _connectslave(int conn_id)
{ int tid = GET_THREAD_ID();
  unsigned t = thread_chans[tid];
  unsigned c = GETR_CHANEND();
  unsigned target_cri = (c & 0xFFFF0000) | (GEN_CHAN_RI(0, 1) & 0xFFFF);
  SETD(t, target_cri);
  OUT(t, t);
  OUTCT_END(t);
  CHKCT_END(t);
  OUTS(t, SLAVE);
  OUTS(t, tid);
  OUTS(t, c);
  OUTS(t, conn_id);
  target_cri = INS(t);
  SETD(c, target_cri);
  return c;
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

/*
 * Thread 0 serve master connection request.
 *  1. Receive channel id
 *  2. Receive master CRI
 *  [queue or complete]
 */
void serveMasterConnReq(unsigned m_thread_cri)
{ unsigned m_chan_cri = INS(conn_master);
  int conn_id = INS(conn_master);
  conn_req s_req;

  // Check if slave side is complete, if not, queue it, otherwise complete.
  if (!dequeueSlaveReq(s_req, conn_id)) 
    queueMasterReq(conn_id, m_thread_cri, m_chan_cri);
  else
  { SETD(conn_master, m_thread_cri);
    OUTS(conn_master, s_req.chan_cri);
    SETD(conn_master, s_req.thread_cri);
    OUTS(conn_master, m_chan_cri);
  }
}

/*
 * Thread 0 serve slave connection request.
 *  1. Receive slave thread id
 *  2. Receive channel id
 *  3. Receive slave CRI
 *  [queue or complete]
 */
void serveSlaveConnReq(unsigned s_thread_cri)
{ unsigned tid = INS(conn_master);
  unsigned s_chan_cri = INS(conn_master);
  int conn_id = INS(conn_master);
  conn_req m_req;

  // Check if master side is complete, if not, queue it, otherwise complete. 
  if (!dequeueMasterReq(m_req, conn_id))
    queueSlaveReq(tid, conn_id, s_thread_cri, s_chan_cri);
  else
  { SETD(conn_master, m_req.thread_cri);
    OUTS(conn_master, s_chan_cri);
    SETD(conn_master, s_thread_cri);
    OUTS(conn_master, m_req.chan_cri);
  }
}

/*
 * Handle an incoming master or slave connection request.
 */
void connHandler()
{ unsigned thread_cri = IN(conn_master);
  CHKCT_END(conn_master);
  SETD(conn_master, thread_cri);
  OUTCT_END(conn_master);
 
  if(INS(conn_master) == MASTER)
    serveMasterConnReq(thread_cri);
  else
    serveSlaveConnReq(thread_cri);
}

