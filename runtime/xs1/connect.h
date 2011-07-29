// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#ifndef CONNECT_H
#define CONNECT_H

void initConnections();
unsigned _connectMaster(int chanid, unsigned dest);
unsigned _connectSlave(int chanid);
void serveConnReq();

#endif
