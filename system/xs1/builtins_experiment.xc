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

extern void _memController(unsigned int input, 
    unsigned int storage, unsigned int base0, unsigned int base);

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

void mix_50_10_40_emulated(unsigned mem, int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    MEM_READ(mem, 2942, v);
    MEM_WRITE(mem, 3259, v);
    MEM_READ(mem, 380, v);
    MEM_WRITE(mem, 1882, v);
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2892, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 604, v);
    MEM_WRITE(mem, 1344, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 725, v);
    MEM_WRITE(mem, 3489, v);
    MEM_READ(mem, 127, v);
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 3981, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    MEM_READ(mem, 1015, v);
    MEM_READ(mem, 1150, v);
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 895, v);
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 1678, v);
    MEM_WRITE(mem, 92, v);
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 3613, v);
    MEM_READ(mem, 1497, v);
    MEM_READ(mem, 2861, v);
    MEM_WRITE(mem, 872, v);
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    MEM_READ(mem, 22, v);
    MEM_READ(mem, 2926, v);
    MEM_WRITE(mem, 3097, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 3373, v);
    MEM_WRITE(mem, 4002, v);
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2, v);
    MEM_READ(mem, 3748, v);
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2369, v);
    MEM_READ(mem, 1906, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 1947, v);
    MEM_WRITE(mem, 48, v);
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 901, v);
    asm("add r0, r0, 0");
  }
  _memFree(p);
}

void mix_50_10_40_normal(int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
  }
  _memFree(p);
}

void mix_34_10_56_emulated(unsigned mem, int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    MEM_READ(mem, 3641, v);
    MEM_WRITE(mem, 3673, v);
    MEM_WRITE(mem, 2236, v);
    asm("add r0, r0, 0");
    MEM_READ(mem, 432, v);
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    MEM_READ(mem, 3634, v);
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    MEM_READ(mem, 578, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 3252, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 3767, v);
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    MEM_WRITE(mem, 1202, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2751, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 242, v);
    MEM_WRITE(mem, 2991, v);
    MEM_WRITE(mem, 3157, v);
    MEM_WRITE(mem, 3489, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 252, v);
    MEM_READ(mem, 3506, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 3173, v);
    MEM_WRITE(mem, 3432, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 627, v);
    MEM_WRITE(mem, 379, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 3125, v);
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 471, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
  }
  _memFree(p);
}

void mix_34_10_56_normal(int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
  }
  _memFree(p);
}

void mix_20_10_70_emulated(unsigned mem, int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 2077, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 554, v);
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 1044, v);
    MEM_WRITE(mem, 1310, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2333, v);
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 690, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    MEM_READ(mem, 2511, v);
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 2125, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 2768, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 1984, v);
    MEM_READ(mem, 2345, v);
    MEM_READ(mem, 3793, v);
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 2973, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
  }
  _memFree(p);
}

void mix_20_10_70_normal(int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
  }
  _memFree(p);
}

void mix_12_10_78_emulated(unsigned mem, int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 3039, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 117, v);
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 2417, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    MEM_WRITE(mem, 667, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2602, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2000, v);
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    MEM_READ(mem, 1771, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
  }
  _memFree(p);
}

void mix_12_10_78_normal(int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
  }
  _memFree(p);
}

void mix_27_10_63_emulated(unsigned mem, int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    MEM_WRITE(mem, 3339, v);
    MEM_WRITE(mem, 1257, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    MEM_READ(mem, 578, v);
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 2052, v);
    MEM_WRITE(mem, 2262, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 2278, v);
    MEM_WRITE(mem, 1306, v);
    asm("add r0, r0, 0");
    MEM_READ(mem, 1523, v);
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    MEM_READ(mem, 2330, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2375, v);
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 3165, v);
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 1433, v);
    MEM_WRITE(mem, 3704, v);
    asm("add r0, r0, 0");
    MEM_READ(mem, 1805, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2059, v);
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_WRITE(mem, 2968, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    MEM_READ(mem, 2005, v);
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
  }
  _memFree(p);
}

void mix_27_10_63_normal(int loop) {
  int v;
  unsigned p;
  _memAlloc(p, 4);
  for(int i=0; i<loop; i++) {
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("stw %0, %1[%2]" :: "r"(v), "r"(p), "r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("ldw %0, %1[%2]":"=r"(v):"r"(p),"r"(0));
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
    asm("add r0, r0, 0");
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
  mix_50_10_40_emulated(mem, LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_34_10_56_emulated(mem, LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_20_10_70_emulated(mem, LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_12_10_78_emulated(mem, LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_27_10_63_emulated(mem, LOOP);
  tmr :> t2;
  printintln(t2 - t1);
}

#define LOOP (10)
void testNormal() {
  timer tmr;
  unsigned t1, t2;
  
  printintln(37);
  
  tmr :> t1;
  mix_50_10_40_normal(LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_34_10_56_normal(LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_20_10_70_normal(LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_12_10_78_normal(LOOP);
  tmr :> t2;
  printintln(t2 - t1);
  
  tmr :> t1;
  mix_27_10_63_normal(LOOP);
  tmr :> t2;
  printintln(t2 - t1);
}
