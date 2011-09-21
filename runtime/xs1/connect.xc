#include <print.h>

#include "util.h"
#include "globals.h"
#include "connect.h"

#define LOCAL_CONNECT_CHAN \
  ((c & 0xFFFF0000) | (GEN_CHAN_RI(0, CONTROL_CONNECT) & 0xFFFF))
#define COMPLETE(c, cri, v) \
  { SETD(c, cri); OUT(c, v); OUTCT_END(c); }
#define NONE (-1)
#define MASTER 0
#define SLAVE  1
#define SERVER 2
#define CLIENT 3 

// Master-slave connection handling
bool dequeueMasterReq(conn_req &r, int connId, int origin);
bool dequeueSlaveReq(conn_req &r, int connId, int origin);
void queueMasterReq(int connId, int origin, unsigned chanCRI);
void queueSlaveReq(unsigned tid, int connId, int origin, unsigned chanCRI);

// Client-server conneciton handling
void openConn(int connId, unsigned chanCRI);
bool getOpenConn(conn_srv &c, int connId);
void queueClientReq(int connId, unsigned chanCRI);
bool dequeueClientReq(conn_req &r, int connId);

/*
 * Complete one side of a connection by sending the CRI of the other party.
 *
inline
void COMPLETE(unsigned c, unsigned cri, unsigned v)
{ SETD(c, cri);
  OUT(c, v);
  OUTCT_END(c);
}*/

/*
 * Initialise the conn_buffer and conn_local arrays.
 */
#pragma unsafe arrays
void initConnections()
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
    conn_buffer[i].connId = NONE;
  for (int i=0; i<MAX_THREADS; i++)
    conn_locals[i].connId = NONE;
  for (int i=0; i<MAX_OPEN_CONNS; i++)
    conn_server[i].connId = NONE;
}

/*
 * Master connection protocol:
 *  0. Get a new channel c and construct target CRI (conn_master).
 *  1. Output channel id on (separate) thread channel t.
 *  2. Output CRI on t.
 *  3. Input slave CRI on t.
 *  4. Set local channel destination of c and return it.
 */
unsigned _connectMaster(int connId, int dest)
{ unsigned c = GETR_CHANEND();
  unsigned destCRI = GEN_CHAN_RI(dest, CONTROL_CONNECT);
  SETD(c, destCRI);
  OUT(c, c);
  OUT(c, MASTER);
  OUT(c, connId);
  OUTCT_END(c);
  destCRI = IN(c);
  CHKCT_END(c);
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
unsigned _connectSlave(int connId, int origin)
{ unsigned c = GETR_CHANEND();
  unsigned destCRI = LOCAL_CONNECT_CHAN;
  SETD(c, destCRI);
  OUT(c, c);
  OUT(c, SLAVE);
  OUT(c, connId);
  OUT(c, origin);
  OUT(c, THREAD_ID());
  OUTCT_END(c);
  destCRI = IN(c);
  CHKCT_END(c);
  SETD(c, destCRI);
  return c;
}

/*
 * Open a server connection for clients to connect to.
 */
unsigned _connectServer(int connId)
{ unsigned c = GETR_CHANEND();
  unsigned destCRI = LOCAL_CONNECT_CHAN;
  SETD(c, destCRI);
  OUT(c, c);
  OUT(c, SERVER);
  OUT(c, connId);
  OUTCT_END(c);
  CHKCT_END(c);
  return c;
}

/*
 * Connect a client to an open server connection.
 */
unsigned _connectClient(int connId, int dest)
{ unsigned c = GETR_CHANEND();
  unsigned destCRI = GEN_CHAN_RI(dest, CONTROL_CONNECT);
  SETD(c, destCRI);
  OUT(c, c);
  OUT(c, CLIENT);
  OUT(c, connId);
  OUTCT_END(c);
  destCRI = IN(c);
  CHKCT_END(c);
  SETD(c, destCRI);
  return c;
}

/*
 * Handle an incoming master or slave connection request.
 *
 * Thread 0 serve master connection request.
 *  1. Receive channel id
 *  2. Receive address of master (origin)
 *  3. Receive master CRI
 *  [queue or complete]
 *
 * Thread 0 serve slave connection request.
 *  1. Receive slave thread id
 *  2. Receive channel id
 *  3. Receive master address (origin)
 *  4. Receive slave CRI
 *  [queue or complete]
 */
void serveConnReq()
{ unsigned chanCRI = IN(conn_master);
  SETD(conn_master, chanCRI);
  
  switch (IN(conn_master))
  { default: 
      ASSERT(0); 
      break;
    case MASTER:
      { int connId = IN(conn_master);
        int origin = GET_GLOBAL_CORE_ID(chanCRI);
        conn_req sReq;
        CHKCT_END(conn_master);
        if (!dequeueSlaveReq(sReq, connId, origin))
          queueMasterReq(connId, origin, chanCRI);
        else
        { COMPLETE(conn_master, chanCRI, sReq.chanCRI);
          COMPLETE(conn_master, sReq.chanCRI, chanCRI);
        }
      }
      break;
    case SLAVE:
      { int connId = IN(conn_master);
        int origin = IN(conn_master);
        int tid = IN(conn_master);
        conn_req mReq;
        CHKCT_END(conn_master);
        if (!dequeueMasterReq(mReq, connId, origin))
          queueSlaveReq(tid, connId, origin, chanCRI);
        else
        { COMPLETE(conn_master, mReq.chanCRI, chanCRI);
          COMPLETE(conn_master, chanCRI, mReq.chanCRI);
        }
      }
      break;
    case SERVER:
      { int connId = IN(conn_master);
        conn_req cReq;
        openConn(connId, chanCRI);
        CHKCT_END(conn_master);
        OUTCT_END(conn_master);
        //printstrln("Opened server connection");
        while(dequeueClientReq(cReq, connId)) 
        { OUT(conn_master, cReq.chanCRI);
          OUTCT_END(conn_master);
          //printstrln("Dequeued client request");
        }
      }
      break;
    case CLIENT:
      { int connId = IN(conn_master);
        conn_srv cOpen;
        CHKCT_END(conn_master);
        if (getOpenConn(cOpen, connId))
        { OUT(conn_master, cOpen.chanCRI);
          OUTCT_END(conn_master);
          //printstrln("Completed client request");
        }
        else
        { queueClientReq(connId, chanCRI);
          //printstrln("Queued client request");
        }
      }
      break;
  }
}

/*
 * Dequeue a master connection request matching the channel id.
 */
bool dequeueMasterReq(conn_req &r, int connId, int origin)
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
  { if (conn_buffer[i].connId == connId 
      && conn_buffer[i].origin == origin)
    { conn_buffer[i].connId = NONE;
      r.chanCRI = conn_buffer[i].chanCRI;
      return true;
    }
  }
  return false;
}

/*
 * Dequeue a slave connection request.
 */
bool dequeueSlaveReq(conn_req &r, int connId, int origin)
{ for (int i=0; i<MAX_THREADS; i++)
  { if (conn_locals[i].connId == connId
      && conn_locals[i].origin == origin)
    { conn_locals[i].connId = NONE;
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
void queueMasterReq(int connId, int origin, unsigned chanCRI)
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
  { if (conn_buffer[i].connId == NONE)
    { conn_buffer[i].connId = connId;
      conn_buffer[i].origin = origin;
      conn_buffer[i].chanCRI = chanCRI;
      return;
    }
  }
  ASSERT(0);
}

/*
 * Queue a slave connection request: insert it in the slot given by the thread
 * id.
 */
void queueSlaveReq(unsigned tid, int connId, int origin, unsigned chanCRI)
{ conn_locals[tid].connId = connId;
  conn_locals[tid].origin = origin;
  conn_locals[tid].chanCRI = chanCRI;
}

/*
 * Open a server connection.
 */
void openConn(int connId, unsigned chanCRI)
{ for (int i=0; i<MAX_OPEN_CONNS; i++)
  { if (conn_server[i].connId == NONE)
    { conn_server[i].connId = connId;
      conn_server[i].chanCRI = chanCRI;
      return;
    }
  }
  ASSERT(0);
}

/*
 * Return the CRI of an open conneciton with a matching conneciton id.
 */
bool getOpenConn(conn_srv &c, int connId)
{ for (int i=0; i<MAX_OPEN_CONNS; i++)
  { if (conn_server[i].connId == connId)
    { c.connId = connId;
      c.chanCRI = conn_server[i].chanCRI;
      return true;
    }
  }
  return false;
}

/*
 * Queue a client conneciton request. This will occur only when a client tries
 * to connect to a server channel before it has opened.
 */
void queueClientReq(int connId, unsigned chanCRI)
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
  { if (conn_buffer[i].connId == NONE)
    { conn_buffer[i].connId = connId;
      conn_buffer[i].chanCRI = chanCRI;
      return;
    }
  }
  ASSERT(0);
}

/*
 * Dequeue and complete any outstanding client-to-server connection requests.
 */
bool dequeueClientReq(conn_req &r, int connId)
{ for (int i=0; i<CONN_BUFFER_SIZE; i++)
  { if (conn_buffer[i].connId == connId) 
    { conn_buffer[i].connId = NONE;
      r.connId = connId;
      r.chanCRI = conn_buffer[i].chanCRI;
      return true;
    }
  }
  return false;
}

