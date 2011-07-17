// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#ifndef CONTROL_H
#define CONTROL_H

/*
 * The control thread is the first thread allocated on each core (with id 0)
 * and is responsible for mediating process creation and channel connections
 * from threads on remote cores to locally executing worker threads.
 */

void controlIdle();
void controlYeild();

#endif

