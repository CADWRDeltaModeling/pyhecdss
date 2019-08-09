%module pyheclib

/* First we'll use the pointer library*/
%include <cpointer.i>
%pointer_functions(int,intp);
%pointer_functions(double,doublep);

/* C arrays */
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

%include "numpy.i"

%init%{
  import_array();
%}

typedef int slen_t;
//
void      chrlnb_(char *cline, int *ilast, slen_t _cline_len);
void      juldat_(int *jul, int *istyle, char *cdate, int *ndate, slen_t _cdate_len);
int       m2ihm_(int *min, char *ctime, slen_t _ctime_len);
void      zcat_(int *ifltab, int *icunit, int *icdunt, int *inunit, char *cinstr, int *labrev, int *ldosrt, int *lcdcat, int *norecs, slen_t _cinstr_len);
void      zdtype_(int *ifltab, char *cpath, int *ndata, int *lfound, char *cdtype, int *idtype, slen_t _cpath_len, slen_t _cdtype_len);
void      zfname_(char *cin, char *cname, int *nname, int *lexist, slen_t _cin_len, slen_t _cname_len);
void      zgintl_(int *intl, char *chintl, int *nodata, int *istat, slen_t _chintl_len);
void      zopen_(int *ifltab, char *cfname, int *istat, slen_t _cfname_len);
void      zset_(char *cflg, char *cstr, int *numb, slen_t _cflg_len, slen_t _cstr_len);
void      zsitsx_(int *ifltab, char *cpath, int *itimes, float *values, int *nvalue, int *ibdate, int *jqual, int *lsqual, char *cunits, char *ctype, int *iuhead, int *nuhead, int *inflag, int *istat, slen_t _cpath_len, slen_t _cunits_len, slen_t _ctype_len);
void      zritsxd_(int *ifltab, char *cpath, int *juls, int *istime, int *jule, int *ietime, int *itimes, double *dvalues, int *kvals, int *nvals, int *ibdate, int *iqual, int *lqual, int *lqread, char *cunits, char *ctype, int *iuhead, int *kuhead, int *nuhead, int *inflag, int *istat, slen_t _cpath_len, slen_t _cunits_len, slen_t _ctype_len);
void      zrpdd_(int *ifltab, char *cpath, int *nord, int *ncurve, int *ihoriz, char *c1unit, char *c1type, char *c2unit, char *c2type, double *dvalues, int *kvals, int *nvals, char *clabel, int *klabel, int *label, int *iuhead, int *kuhead, int *nuhead, int *istat, slen_t _cpath_len, slen_t _c1unit_len, slen_t _c1type_len, slen_t _c2unit_len, slen_t _c2type_len, slen_t _clabel_len);
%cstring_bounded_output(char* cunits, 8);
%cstring_bounded_output(char* ctype, 8);
void      zrrtsx_(int *ifltab, char *cpath, char *cdate, char *ctime, int *nvals, float *svalues, int *jqual, int *lqual, int *lqread, char *cunits, char *ctype, int *iuhead, int *kuhead, int *nuhead, int *iofset, int *jcomp, int *istat, slen_t _cpath_len, slen_t _cdate_len, slen_t _ctime_len, slen_t _cunits_len, slen_t _ctype_len);
void      zrrtsxd_(int *ifltab, char *cpath, char *cdate, char *ctime, int *nvals, double *dvalues, int *jqual, int *lqual, int *lqread, char *cunits, char *ctype, int *iuhead, int *kuhead, int *nuhead, int *iofset, int *jcomp, int *istat, slen_t _cpath_len, slen_t _cdate_len, slen_t _ctime_len, slen_t _cunits_len, slen_t _ctype_len);
%apply (double* INPLACE_ARRAY1, int DIM1) {(double* numpyvalues, int nvals)};
%include "hecwrapper.h";
%clear (double* numpyvalues, int nvals);
void      zclose_(int *ifltab);
int       fortranclose_(int *INPUT);
void      fortranflush_(int *INPUT);
int       fortranopen_(int *INPUT, char *filename, slen_t _filename_len);
//Heclib.makedsscatalog
//Heclib.closescratchdsscatalog
//Heclib.getEPartFromInterval = zgintl_+chrlnb_
