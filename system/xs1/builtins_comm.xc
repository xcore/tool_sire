#define _INP(c, v)    asm volatile("in %0, res[%1]" : "=r"(v) : "r"(c))
#define _OUT(c, v)    asm volatile("out res[%0], %1" :: "r"(c), "r"(v))
#define _INPT(c, v)   asm volatile("int %0, res[%1]" : "=r"(v) : "r"(c))
#define _OUTT(c, v)   asm volatile("outt res[%0], %1" :: "r"(c), "r"(v))
#define _INCT(c, v)   asm volatile("inct %0, res[%1]" : "=r"(v) : "r"(c))
#define _OUTCT(c, v)  asm volatile("outct res[%0], %1" :: "r"(c), "r"(v))
#define _CHKCTACK(c)  asm volatile("chkct res[%0]," S(XS1_CT_ACK) :: "r"(c))
#define _OUTCTACK(c)  asm volatile("outct res[%0]," S(XS1_CT_ACK) :: "r"(c))
#define _CHKCTEND(c)  asm volatile("chkct res[%0]," S(XS1_CT_END) :: "r"(c))
#define _OUTCTEND(c)  asm volatile("outct res[%0]," S(XS1_CT_END) :: "r"(c))
#define _SETD(c, v)   asm volatile("setd  res[%0], %1" :: "r"(c), "r"(v))
#define _GETCID(c, v) do { v = c; } while(0);
#define _FREER(c)     asm volatile("freer res[%0]" :: "r"(c))
