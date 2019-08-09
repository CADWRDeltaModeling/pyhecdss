#include "hecwrapper.h"
void hec_zrrtsxd(int *ifltab, char *cpath, char *cdate, char *ctime, double* numpyvalues, int nvals, int *jqual, int *lqual, int *lqread, char *cunits, char *ctype, int *iuhead,
  int *kuhead, int *nuhead, int *iofset, int *jcomp, int *istat, slen_t _cpath_len, slen_t _cdate_len, slen_t _ctime_len, slen_t _cunits_len, slen_t _ctype_len){
  zrrtsxd_(ifltab, cpath, cdate, ctime, &nvals, numpyvalues, jqual, lqual, lqread, cunits, ctype, iuhead, kuhead, nuhead, iofset, jcomp, istat, _cpath_len, _cdate_len, _ctime_len, _cunits_len, _ctype_len);
}
