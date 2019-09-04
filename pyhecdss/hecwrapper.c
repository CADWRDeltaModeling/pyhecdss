#include "hecwrapper.h"
// julian days since 31DEC1899 2400
void hec_datjul(char *cdate,  slen_t _cdate_len, int *jul, int *ierr){
  datjul_(cdate, jul, ierr, _cdate_len);
}
//
void hec_zopen(int *ifltab, char *cfname, int cflen, int *istat){
  zopen_(ifltab, cfname, istat, cflen);
}
// inquire about parameters
void hec_zinqir(int *ifltab, char *cflg, slen_t _cflg_len, char *calpha, slen_t _calpha_len, int *inumb){
  zinqir_(ifltab, cflg, calpha, inumb, _cflg_len, _calpha_len);
}
// versioning info for filename
void hec_zfver(char *cfname, slen_t _cfname_len, char *cver, int *iver){
  slen_t _cver_len=4; // refer to pyheclib.i for length match
  zfver_(cfname, cver, iver, _cfname_len, _cver_len);
}
// set params
void hec_zset(char *cflg, slen_t _cflg_len, char *cstr,  slen_t _cstr_len, int *numb){
  zset_(cflg, cstr, numb, _cflg_len, _cstr_len);
}
// E part  <--> interval conversions
void hec_zgintl(int *intl, char *chintl,slen_t _chintl_len, int *nodata, int *istat){
  zgintl_(intl, chintl, nodata, istat, _chintl_len);
}
//Store reqular time series
void hec_zsrtsxd(int *ifltab,
    char *cpath, slen_t _cpath_len,
    char *cdate, slen_t _cdate_len,
    char *ctime, slen_t _ctime_len,
    double *numpyvalues, int nvals,
    char *cunits,  slen_t _cunits_len,
    char *ctype, slen_t _ctype_len,
    int *istat){
      int jqual=0, lqual=0;
      int iuhead=0,nuhead=0;
      int iplan=0; // always overwrite (using merging functions)
      int jcomp=0; // default compression, next few are for compression
      float basev=0;
      int lbasev=0,ldhigh=0, nprec=0;
      zsrtsxd_(ifltab,
        cpath, cdate, ctime,
        &nvals, numpyvalues,
        &jqual,  &lqual,
        cunits, ctype,
        &iuhead, &nuhead,
        &iplan, &jcomp,
        &basev, &lbasev, &ldhigh, &nprec,
        istat,
         _cpath_len,  _cdate_len,  _ctime_len,  _cunits_len,  _ctype_len);
}
//Store irregular time series
void hec_zsitsxd(int *ifltab,
  char *cpath, slen_t _cpath_len,
  int *itimes, int ntvalue,
  double *dvalues, int ndvalue,
  int *ibdate,
  char *cunits, slen_t _cunits_len,
  char *ctype,  slen_t _ctype_len,
  int *inflag,
  int *istat){
        int jqual=0, lsqual=0;
        int iuhead=0,nuhead=0;
        //check that ntvalue == ndvalue
        zsitsxd_(ifltab,
           cpath, itimes, dvalues, &ndvalue, ibdate, &jqual, &lsqual, cunits, ctype, &iuhead, &nuhead, inflag, istat, _cpath_len, _cunits_len, _ctype_len);
}

// return the number of values read
int hec_zrrtsxd(int *ifltab,
  char *cpath, slen_t _cpath_len,
  char *cdate, slen_t _cdate_len,
  char *ctime, slen_t _ctime_len,
  double *numpyvalues, int nvals,
  char *cunits, char *ctype,
  int *iofset, int *istat) {
  slen_t _cunits_len=8;//FIXME: This should match the pyheclib.i definitions
  slen_t _ctype_len=8;
  int jqual = 0;
  int lqual = 0;
  int lqread = 0;
  int iuhead = 0;
  int kuhead = 0;
  int nuhead = 0;
  int jcomp=0;
  zrrtsxd_(ifltab, cpath, cdate, ctime, &nvals, numpyvalues,
    &jqual, &lqual, &lqread, cunits, ctype, &iuhead, &kuhead, &nuhead, iofset, &jcomp, istat,
    _cpath_len, _cdate_len, _ctime_len, _cunits_len, _ctype_len);
  return nvals;
}

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
   int *istat){
  slen_t _cunits_len=8;//FIXME: This should match the pyheclib.i definitions
  slen_t _ctype_len=8;
  int iqual = 0;
  int lqual = 0;
  int lqread = 0;
  int iuhead = 0;
  int kuhead = 0;
  int nuhead = 0;
  //check that ntvalue == ndvalue
  zritsxd_(ifltab, cpath, juls, istime, jule, ietime,
    itimes, dvalues, &ktvals,
    nvals, ibdate,
    &iqual, &lqual, &lqread, cunits, ctype, &iuhead, &kuhead, &nuhead,
    inflag, istat, _cpath_len, _cunits_len, _ctype_len);

}
