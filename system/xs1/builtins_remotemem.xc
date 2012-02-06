#define _RWRITE(destID, address, value) \
do { \
  unsigned c; \
  GETR_CHANEND(c); \
  SETD(c, destID << 16 | XS1_RES_TYPE_CHANEND); \
  OUTCT(c, XS1_CT_WRITE4); \
  OUT(c, address); \
  OUT(c, value); \
  OUTCT_END(c); \
  CHKCT_END(c); \
  FREER(c); \
} while(0)
#define _RREAD(destID, address, value) \
do { \
  unsigned c; \
  GETR_CHANEND(c); \
  SETD(c, destID << 16 | XS1_RES_TYPE_CHANEND); \
  OUTCT(c, XS1_CT_READ4); \
  OUT(c, address); \
  OUTCT_END(c); \
  IN(c, value); \
  CHKCT_END(c); \
  FREER(c); \
} while(0)
