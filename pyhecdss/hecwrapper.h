#ifndef __HEC_WRAPPER_H__
#define __HEC_WRAPPER_H__
/*
* The header file for wrapping C functions to order and types friendlier to
* SWIG typemaps.
*
*/
#include "heclib.h"
// julian days since 31DEC1899 2400
void hec_datjul(char *cdate,  slen_t _cdate_len, int *jul, int *ierr);
// open dss file
void hec_zopen(int *ifltab, char *cfname, int cflen, int *istat);
// inquire about parameters
void hec_zinqir(int *ifltab, char *cflg, slen_t _cflg_len, char *calpha, slen_t _calpha_len, int *inumb);
// set params
void hec_zset(char *cflg, slen_t _cflg_len, char *cstr,  slen_t _cstr_len, int *numb);
// versioning info for filename
void hec_zfver(char *cfname, slen_t _cfname_len, char *cver, int *iver);
// E part  <--> interval conversions
void hec_zgintl(int *intl, char *chintl,slen_t _chintl_len, int *nodata, int *istat);
// Store regular time series
void hec_zsrtsxd(int *ifltab,
    char *cpath, slen_t _cpath_len,
    char *cdate, slen_t _cdate_len,
    char *ctime, slen_t _ctime_len,
    double *numpyvalues, int nvals,
    char *cunits,  slen_t _cunits_len,
    char *ctype, slen_t _ctype_len,
    int *istat);
//Store irregular time series
void hec_zsitsxd(int *ifltab,
  char *cpath, slen_t _cpath_len,
  int *itimes, int ntvalue,
  double *dvalues, int ndvalue,
  int *ibdate,
  char *cunits, slen_t _cunits_len,
  char *ctype,  slen_t _ctype_len,
  int *inflag,
  int *istat);
// Retrieve regular time series
// returns nvals (number of values read as contrasted to requested)
int hec_zrrtsxd(int *ifltab,
  char *cpath, slen_t _cpath_len,
  char *cdate, slen_t _cdate_len,
  char *ctime, slen_t _ctime_len,
  double *numpyvalues, int nvals,
  char *cunits, char *ctype,
  int *iofset, int *istat);
// Retrieve irregular time series
void hec_zritsxd(int *ifltab,
   char *cpath, slen_t _cpath_len,
   int *juls, int *istime,
   int *jule, int *ietime,
   int *itimes, int ktvals,
   double *dvalues, int kdvals,
   int *nvals,
   int *ibdate,
   char *cunits,
   char *ctype,
   int *inflag,
   int *istat);

#endif
