#define _RWRITE(destID, address, value) \
do { \
  unsigned c = chan_mem_access; \
  SETD(c, destID<<16 | CHAN_ID_MEM_ACCESS<<8 | XS1_RES_TYPE_CHANEND); \
  OUTCT(c, XS1_CT_WRITE4); \
  OUT(c, c); \
  OUT(c, address); \
  OUT(c, value); \
  OUTCT_END(c); \
  CHKCT_END(c); \
} while(0)
#define _RREAD(destID, address, value) \
do { \
  unsigned c = chan_mem_access; \
  SETD(c, destID<<16 | CHAN_ID_MEM_ACCESS<<8 | XS1_RES_TYPE_CHANEND); \
  OUTCT(c, XS1_CT_READ4); \
  OUT(c, c); \
  OUT(c, address); \
  OUTCT_END(c); \
  IN(c, value); \
  CHKCT_END(c); \
} while(0)
