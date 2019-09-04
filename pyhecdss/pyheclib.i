%module pyheclib

/* First we'll use the pointer library*/
%include <cpointer.i>
%pointer_functions(int,intp);
%pointer_functions(double,doublep);

/* C arrays -- prefer numpy mapping if possible. */
%include "carrays.i"
%array_class(int, intArray);
%array_class(double, doubleArray);

/* strings */
%include "cstring.i"

%{
#define SWIG_FILE_WITH_INIT
#include "heclib.h"
#include "hecwrapper.h"
%}

%include <typemaps.i>

// numpy mappings -- copied from numpy 1.15 -- upgrade only if needed
%include "numpy.i"

%init%{
  import_array();
%}

typedef int slen_t;
// -- straight up heclib functions
void      zcat_(int *ifltab, int *icunit, int *icdunt, int *inunit, char *cinstr, int *labrev, int *ldosrt, int *lcdcat, int *norecs, slen_t _cinstr_len);
int       fortranclose_(int *INPUT);
void      fortranflush_(int *INPUT);
int       fortranopen_(int *INPUT, char *filename, slen_t _filename_len);
void      zclose_(int *ifltab);

/*
* wrapper functions mappings. This is done to usually rearrange arguments so
* that they fit one of the defined typemaps from swig or numpy.i
*/

%apply (int *OUTPUT) { int *jul };
%apply (int *OUTPUT) { int *ierr };
%apply (char *STRING, int LENGTH) { (char *cdate,  slen_t _cdate_len) };
void hec_datjul(char *cdate,  slen_t _cdate_len, int *jul, int *ierr);
%apply (char *STRING, int LENGTH) { (char *cflg, slen_t _cflg_len) };
%apply (char *STRING, int LENGTH) { (char *cstr, slen_t _cstr_len) };

// versioning info for filename
%apply (char *STRING, int LENGTH) { (char *cfname, slen_t _cfname_len) };
%cstring_bounded_output(char *cver, 4);
%apply (int *OUTPUT) { int *iver };
void hec_zfver(char *cfname, slen_t _cfname_len, char *cver, int *iver);
%apply (int *OUTPUT) { int *numb };
%cstring_bounded_output(char *calpha, 80);
%apply (char *STRING, int LENGTH) { (char *calpha, slen_t _calpha_len) };
void hec_zinqir(int *ifltab, char *cflg, slen_t _cflg_len, char *calpha, slen_t _calpha_len, int *inumb);
%clear (int *numb);
%apply (int *INPUT) { int *numb };
void hec_zset(char *cflg, slen_t _cflg_len, char *cstr,  slen_t _cstr_len, int *numb);
%apply (int *INOUT) { int *intl};
%cstring_bounded_mutable(chintl, 32);
%apply (char *STRING, int LENGTH) { (char *chintl, slent_t _chintl_len) };
%apply (int *INOUT) { int *istat };
%apply (int *OUTPUT) { int *nodata };
void hec_zgintl(int *intl, char *chintl, slen_t _chintl_len, int *nodata, int *istat);
%clear (int *nodata);
// 4 to allow extension of ".dss" to be added to cfname if needed
%cstring_bounded_mutable(cfname, 4);
%apply ( int *OUTPUT ) { int *iofset };
%apply ( int *OUTPUT ) { int *istat };
%apply (double* INPLACE_ARRAY1, int DIM1) {(double *numpyvalues, int nvals)};
%apply (char *STRING, int LENGTH) { (char *cfname, int cflen) };
%apply (char *STRING, int LENGTH) { (char *cpath, slen_t _cpath_len) };
%apply (char *STRING, int LENGTH) { (char *cdate, slen_t _cdate_len) };
%apply (char *STRING, int LENGTH) { (char *ctime, slen_t _ctime_len) };
void hec_zopen(int *ifltab, char *cfname, int cflen, int *istat);
%apply (char *STRING, int LENGTH) { (char *cunits,  slen_t _cunits_len) };
%apply (char *STRING, int LENGTH) { (char *ctype, slen_t _ctype_len) };
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
%apply (double* INPLACE_ARRAY1, int DIM1) {(double *dvalues, int ndvalue)};
%apply (int* INPLACE_ARRAY1, int DIM1) {(int *itimes, int ntvalue)};
%apply (int *INPUT) { int *ibdate};
%apply ( int *INPUT ) { int *inflag };
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
%clear (char *cunits,  slen_t _cunits_len);
%clear (char *ctype, slen_t _ctype_len);
%cstring_bounded_output(char *cunits, 8);
%cstring_bounded_output(char *ctype, 8);
int hec_zrrtsxd(int *ifltab,
  char *cpath, slen_t _cpath_len,
  char *cdate, slen_t _cdate_len,
  char *ctime, slen_t _ctime_len,
  double *numpyvalues, int nvals,
  char *cunits, char *ctype,
  int *iofset, int *istat);
%apply ( int *INPUT ) { int *juls };
%apply ( int *INPUT ) { int *istime };
%apply ( int *INPUT ) { int *jule };
%apply ( int *INPUT ) { int *ietime };
// Retrieve irregular time series
%apply (int* INPLACE_ARRAY1, int DIM1) {(int *itimes, int ktvals)};
%apply (double* INPLACE_ARRAY1, int DIM1) {(double *dvalues, int kdvals)};
%apply (int *OUTPUT) { int *nvals};
%apply (int *OUTPUT) { int *ibdate};
%apply ( int *INPUT ) { int *inflag };
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
//%clear (double* numpyvalues, int nvals);
