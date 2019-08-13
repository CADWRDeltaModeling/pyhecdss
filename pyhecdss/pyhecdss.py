from . import pyheclib
import pandas as pd
import numpy as np
import os
import time
class DSSFile:
    #DSS missing conventions
    MISSING_VALUE=-901.0
    MISSING_RECORD=-902.0
    def __init__(self,fname):
        self.ifltab=pyheclib.intArray(600)
        self.istat=pyheclib.new_intp()
        self.fname=fname
        self.isopen=False
    def open(self):
        """
        Open DSS file
        """
        if (self.isopen): return
        pyheclib.zopen_(self.ifltab,self.fname,self.istat,len(self.fname))
        self.isopen=True
    def close(self):
        """
        Close DSS File
        """
        #FIXME: remove all created arrays and pointers
        if (self.isopen):
            pyheclib.zclose_(self.ifltab)
            self.isopen=False
    def get_version(self):
        """
        Get version of DSS File
        """
        #needs to be done on a closed file
        if (self.isopen): self.close()
        pyheclib.zfver_(self.fname, char *cver, int *iver, len(fname), len(cver));
    def catalog(self):
        """
        Catalog DSS Files
        """
        try:
            self.open()
            icunit=pyheclib.new_intp() # unit (fortran) for catalog
            pyheclib.intp_assign(icunit,12)
            fcname=self.fname[:self.fname.rfind(".")]+".dsc"
            pyheclib.fortranopen_(icunit,fcname, len(fcname))
            icdunit=pyheclib.new_intp() # unit (fortran) for condensed catalog
            fdname=self.fname[:self.fname.rfind(".")]+".dsd"
            pyheclib.intp_assign(icdunit,13)
            pyheclib.fortranopen_(icdunit,fdname,len(fdname))
            inunit=pyheclib.new_intp()
            pyheclib.intp_assign(inunit,0) # new catalog, if non-zero no cataloging
            cinstr="" # catalog instructions : None = ""
            labrev = pyheclib.new_intp()
            pyheclib.intp_assign(labrev,0) # 0 is unabbreviated.
            ldsort = pyheclib.new_intp()
            pyheclib.intp_assign(ldsort,1) # 1 is sorted
            lcdcat = pyheclib.new_intp() # output if condensed created
            nrecs = pyheclib.new_intp() # number of records cataloged
            pyheclib.zcat_(self.ifltab, icunit, icdunit, inunit, cinstr,
                labrev, ldsort, lcdcat, nrecs, len(cinstr))
            return pyheclib.intp_value(nrecs)
        except:
            pass
        finally:
            pyheclib.fortranflush_(icunit)
            pyheclib.fortranclose_(icunit)
            pyheclib.fortranflush_(icdunit)
            pyheclib.fortranclose_(icdunit)
            pyheclib.fortranflush_(inunit)
            pyheclib.fortranclose_(inunit)
            self.close()
    def read_catalog(self):
        """
        Reads .dsd (condensed catalog) for the given dss file.
        Will run catalog if it doesn't exist or is out of date
        """
        fdname=self.fname[:self.fname.rfind(".")]+".dsd"
        if not os.path.exists(fdname):
            print("NO CATALOG FOUND: Generating...")
            self.catalog()
        else:
            if os.path.exists(self.fname):
                ftime=pd.to_datetime(time.ctime(os.path.getmtime(self.fname)))
                fdtime=pd.to_datetime(time.ctime(os.path.getmtime(fdname)))
                if ftime > fdtime:
                    print("CATALOG FILE OLD: Generating...")
                    self.catalog()
            else:
                print("Warning: No DSS File found. Using catalog file as is")
        #
        with open(fdname,'r') as fd:
            lines=fd.readlines()
        columns=['Tag','A Part','B Part','C Part','F Part','E Part','D Part']
        colline=lines[7]
        column_indices=[]
        for c in columns:
            column_indices.append(colline.find(c))
        a=np.empty([len(columns),len(lines)-9],dtype='U132')
        ilx=0
        for line in lines[9:]:
            cix=0
            isx=column_indices[0]
            for iex in column_indices[1:]:
                s=line[isx:iex].strip()
                if s.startswith("-"):
                    s=a[cix,ilx-1]
                a[cix,ilx]=s
                cix=cix+1
                isx=iex
            s=line[isx:].strip()
            a[cix,ilx]=s
            ilx=ilx+1
        df=pd.DataFrame(a.transpose(),columns=list('TABCFED'))
        return df
    def get_pathnames(self,catalog_dataframe=None):
        """
        converts a catalog data frame into pathnames
        If catalog_dataframe is None then reads catalog to populate it

        returns a list of pathnames (condensed version, i.e. D part is time window)
        /A PART/B PART/C PART/DPART (START DATE "-" END DATE)/E PART/F PART/
        """
        if catalog_dataframe is None:
            catalog_dataframe=self.read_catalog()
        pdf=catalog_dataframe.iloc[:,[1,2,3,6,5,4]]
        return pdf.apply(func=lambda x: '/'+('/'.join(x.to_list()))+'/',axis=1).to_list()
    def num_values_in_interval(self,sdstr,edstr,istr):
        """
        Get number of values in interval istr, using the start date and end date
        string
        """
        return int((pd.to_datetime(edstr)-pd.to_datetime(sdstr))/pd.to_timedelta(istr))
    def julian_day(self, date):
        """
        get julian day for the date. (count of days since beginning of year)
        """
        return xxx
    def m2ihm(self, minute):
        """
        24 hour style from mins
        """
        ihr=minute/60
        imin=minute-(ihr*60)
        itime=ihr*100+min
        return itime
    def parse_pathname_epart(self,pathname):
        return pathname.split('/')[1:7][4]
    def read_rts(self,pathname,startDateStr=None, endDateStr=None):
        """
        read regular time series for pathname.
        if pathname D part contains a time window (START DATE "-" END DATE) and
        either start or end date is None it uses that to define start and end date
        """
        try:
            self.open()
            interval = self.parse_pathname_epart(pathname)
            if startDateStr is None or endDateStr is None:
                twstr=pathname.split("/")[4]
                if twstr.find("-") < 0 :
                    raise "No start date or end date and twstr is "+twstr
                sdate,edate=twstr.split("-")
                if startDateStr is None:
                    startDateStr=sdate.strip()
                if endDateStr is None:
                    endDateStr=edate.strip()
            nvals = self.num_values_in_interval(startDateStr, endDateStr, interval)
            sdate = pd.to_datetime(startDateStr)
            cdate = sdate.date().strftime('%d%b%Y').upper()
            ctime = ''.join(sdate.time().isoformat().split(':')[:2])
            dvalues = np.array(range(nvals),'d')
            jqual=pyheclib.new_intp()
            lqual=pyheclib.new_intp()
            lqread=pyheclib.new_intp()
            iuhead=pyheclib.new_intp()
            kuhead=pyheclib.new_intp()
            nuhead=pyheclib.new_intp()
            iofset=pyheclib.new_intp()
            jcomp=pyheclib.new_intp()
            istat=pyheclib.new_intp()
            pyheclib.intp_assign(kuhead,0)
            pyheclib.intp_assign(lqual,0)
            _cpath_len=len(pathname)
            _cdate_len=len(cdate)
            _ctime_len=len(ctime)
            _cunits_len=8
            _ctype_len=8
            cunits,ctype=pyheclib.hec_zrrtsxd(self.ifltab, pathname, cdate, ctime,
                dvalues,
                jqual, lqual, lqread, iuhead, kuhead, nuhead, iofset, jcomp, istat,
                 _cpath_len, _cdate_len, _ctime_len, _cunits_len, _ctype_len)
            pyheclib.delete_intp(jqual)
            pyheclib.delete_intp(lqual)
            pyheclib.delete_intp(lqread)
            pyheclib.delete_intp(iuhead)
            pyheclib.delete_intp(kuhead)
            pyheclib.delete_intp(nuhead)
            pyheclib.delete_intp(iofset)
            pyheclib.delete_intp(jcomp)
            pyheclib.delete_intp(istat)
            dindex=pd.date_range(startDateStr,periods=nvals,freq=interval)
            df1=pd.DataFrame(data=dvalues,index=dindex,columns=[pathname])
            df1.replace([DSSFile.MISSING_VALUE,DSSFile.MISSING_RECORD],[np.nan,np.nan],inplace=True)
            return df1,cunits.strip(),ctype.strip()
        finally:
            self.close()
