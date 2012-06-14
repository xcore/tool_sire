#define ADDR_LEN   30
#define ADDR_MASK  0x3FFFFFFF
#define QUERY_MASK 0xC0000000
#define READ       (0x1 << ADDR_LEN)
#define WRITE      (0x2 << ADDR_LEN)
#define HALT       (0x3 << ADDR_LEN)
#define READY      (0x4 << ADDR_LEN)

#define MEM_READ(c, index, value) \
do { \
  OUT(c, READ | index); \
  OUTCT_END(c); \
  CHKCT_END(c); \
  IN(c, value); \
  CHKCT_END(c); \
  OUTCT_END(c); \
} while(0)

#define MEM_WRITE(c, index, value) \
do { \
  OUT(c, WRITE | index); \
  OUTCT_END(c); \
  CHKCT_END(c); \
  OUT(c, value); \
  OUTCT_END(c); \
  CHKCT_END(c); \
} while(0)

#define _MEM_READ_TIMED(c, index, value, time) \
do { \
  unsigned t1, t2; \
  _TIME(t1); \
  MEM_READ(c, index, value); \
  _TIME(t2); \
  time = t2 - t1; \
} while(0)

#define _MEM_WRITE_TIMED(c, index, value, time) \
do { \
  unsigned t1, t2; \
  _TIME(t1); \
  MEM_WRITE(c, index, value); \
  _TIME(t2); \
  time = t2 - t1; \
} while(0)

//#define LEN 1001
///*#define ADDR_x 0
//#define ADDR_y LEN
//#define ADDR_z (2*LEN)
//#define ADDR_v (3*LEN)*/
//#define ADDR_x 0
//#define ADDR_y 1024
//#define ADDR_z 0
//#define ADDR_v 1024
//
///*
// *******************************************************************
// *   Kernel 1 -- hydro fragment
// *******************************************************************
// */
//
//// r
//// t
//// q
//// x[1001]
//// y[1001]
//// z[1001]
//
//void livermore1(unsigned mem, int loop, int n) {
//  int l, k;
//  int q = 1;
//  int r = 1;
//  int t = 1;
//  for ( l=1 ; l<=loop ; l++ ) {
//    for ( k=0 ; k<n ; k++ ) {
//      //x[k] = q + y[k]*( r*z[k+10] + t*z[k+11] );
//      int t1, t2, t3;
//      MEM_READ(mem, ADDR_y+k, t1);
//      MEM_READ(mem, ADDR_z+k+10, t2);
//      MEM_READ(mem, ADDR_z+k+11, t3);
//      MEM_WRITE(mem, ADDR_x+k, q + t1*(r*t2 + t*t3));
//    }
//  }
//}
//
///*
// *******************************************************************
// *   Kernel 2 -- ICCG excerpt (Incomplete Cholesky Conjugate Gradient)
// *******************************************************************
// */
//
//// x[1001]
//// v[1001]
//void livermore2(unsigned mem, int n, int loop) {
//  int k, l;
//  int i, ii, ipntp, ipnt;
//  for ( l=1 ; l<=loop ; l++ ) {
//    ii = n;
//    ipntp = 0;
//    do {
//      ipnt = ipntp;
//      ipntp += ii;
//      ii /= 2;
//      i = ipntp - 1;
//      for ( k=ipnt+1 ; k<ipntp ; k=k+2 ) {
//        int t1, t2, t3, t4, t5;
//        i++;
//        //x[i] = x[k] - v[k  ]*x[k-1] - v[k+1]*x[k+1];
//        MEM_READ(mem, ADDR_x+k, t1);
//        MEM_READ(mem, ADDR_v+k, t2);
//        MEM_READ(mem, ADDR_x+k-1, t3);
//        MEM_READ(mem, ADDR_v+k+1, t4);
//        MEM_READ(mem, ADDR_x+k+1, t5);
//        MEM_WRITE(mem, ADDR_x+i, t1-(t2*t3)-(t4*t5));
//      }
//    } while ( ii>0 );
//  }
//}
//
///*
// *******************************************************************
// *   Kernel 3 -- inner product
// *******************************************************************
// */
//
//// x[1001]
//// z[1001]
//int livermore3(unsigned mem, int n, int loop) {
//  int l, k;
//  int q;
//  for ( l=1 ; l<=loop ; l++ ) {
//    q = 0;
//    for ( k=0 ; k<n ; k++ ) {
//      //q += z[k]*x[k];
//      int t1, t2;
//      MEM_READ(mem, ADDR_z+k, t1);
//      MEM_READ(mem, ADDR_x+k, t2);
//      q += t1*t2;
//    }
//  }
//  // Otherwise most of this gets optimised away
//  return q;
//}
//
///*
// *******************************************************************
// *   Kernel 4 -- banded linear equations
// *******************************************************************
// */
//
//void livermore4(unsigned mem, int n, int loop) {
//  int j, k, l;
//  int m, lw, temp;
//  m = ( 1001-7 )/2;
//  for ( l=1 ; l<=loop ; l++ ) {
//    for ( k=6 ; k<1001 ; k=k+m ) {
//      int t1;
//      lw = k - 6;
//      //temp = x[k-1];
//      MEM_READ(mem, ADDR_x+k-1, temp);
//      for ( j=4 ; j<n ; j=j+5 ) {
//        int t2;
//        //temp -= x[lw]*y[j];
//        MEM_READ(mem, ADDR_x+lw, t1);
//        MEM_READ(mem, ADDR_y+j, t2);
//        temp -= t1*t2;
//        lw++;
//      }
//      //x[k-1] = y[4]*temp;
//      MEM_READ(mem, ADDR_y+4, t1);
//      MEM_WRITE(mem, ADDR_x+k-1, t1*temp);
//    }
//  }
//}
//
///*
// *******************************************************************
// *   Kernel 5 -- tri-diagonal elimination, below diagonal
// *******************************************************************
// */
//
//void livermore5(unsigned mem, int n, int loop) {
//  int i, l;
//  for ( l=1 ; l<=loop ; l++ ) {
//    for ( i=1 ; i<n ; i++ ) {
//      int t1, t2, t3;
//      //x[i] = z[i]*( y[i] - x[i-1] );
//      MEM_READ(mem, ADDR_z+i, t1);
//      MEM_READ(mem, ADDR_y+i, t2);
//      MEM_READ(mem, ADDR_x+i-1, t3);
//      MEM_WRITE(mem, ADDR_x+i, t1*(t2-t3));
//    }
//  }
//}

void mix_1_1_emulated(unsigned mem, int loop) {
  int v;
  for(int i=0; i<loop; i++) {
    MEM_WRITE(mem, 5, v);
    asm("add r0, r0, 0");
    MEM_READ(mem, 399, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2013, v);
    asm("add r0, r0, 0");
    MEM_READ(mem, 1994, v);
    MEM_WRITE(mem, 1755, v);
    MEM_WRITE(mem, 1538, v);
    MEM_WRITE(mem, 1583, v);
    MEM_READ(mem, 1240, v);
    MEM_WRITE(mem, 382, v);
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 1978, v);
    asm("add r0, r0, 0");
    MEM_READ(mem, 1952, v);
    MEM_READ(mem, 215, v);
    MEM_WRITE(mem, 1588, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 1274, v);
    asm("add r0, r0, 0");
    MEM_READ(mem, 1380, v);
    MEM_READ(mem, 737, v);
    MEM_READ(mem, 307, v);
    asm("add r0, r0, 0");
    MEM_READ(mem, 283, v);
    MEM_READ(mem, 275, v);
    MEM_READ(mem, 335, v);
    MEM_READ(mem, 569, v);
  }
}

void mix_1_1_normal(int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
  }
  _memFree(p);
}

void mix_1_2_emulated(unsigned mem, int loop) {
  int v;
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 109, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 277, v);
    MEM_WRITE(mem, 82, v);
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 1227, v);
    MEM_WRITE(mem, 1229, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 431, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 1115, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 1627, v);
    MEM_WRITE(mem, 1515, v);
    asm("add r0, r0, 0");
    MEM_READ(mem, 1914, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 1217, v);
  }
}

void mix_1_2_normal(int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
  }
  _memFree(p);
}


void mix_1_3_emulated(unsigned mem, int loop) {
  int v;
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 831, v);
    MEM_READ(mem, 1258, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 1552, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 968, v);
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 292, v);
    MEM_READ(mem, 842, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 1932, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 1330, v);
    MEM_WRITE(mem, 1540, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 1771, v);
  }
}

void mix_1_3_normal(int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]" : "=r"(v) : "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
  }
  _memFree(p);
}

#define LOOP (10)
void testEmulated(unsigned mem) {
  timer tmr;
  unsigned t1, t2;

  //unsigned v;
  //MEM_READ(mem, 1721, v);
  //MEM_WRITE(mem, 7, v);
  //MEM_READ(mem, 1721, v);
  //MEM_WRITE(mem, 7, v);

  tmr :> t1;
  mix_1_1_emulated(mem, LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_1_2_emulated(mem, LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_1_3_emulated(mem, LOOP);
  tmr :> t2;
  printintln(t2 - t1);
}

#define LOOP (10)
void testNormal() {
  timer tmr;
  unsigned t1, t2;
  
  printintln(37);
  
  tmr :> t1;
  mix_1_1_normal(LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_1_2_normal(LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_1_3_normal(LOOP);
  tmr :> t2;
  printintln(t2 - t1);
}
