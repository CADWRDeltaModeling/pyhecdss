#include "heclib.h"
#ifndef __HEC_WRAPPER_H__
#define __HEC_WRAPPER_H__
//
void hec_zrrtsxd(int *ifltab, char *cpath, char *cdate, char *ctime,
  double* numpyvalues, int nvals,
  int *jqual, int *lqual, int *lqread, char *cunits, char *ctype,
  int *iuhead, int *kuhead, int *nuhead, int *iofset, int *jcomp, int *istat,
  slen_t _cpath_len, slen_t _cdate_len, slen_t _ctime_len, slen_t _cunits_len, slen_t _ctype_len);
#endif
