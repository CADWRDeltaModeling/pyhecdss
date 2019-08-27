from . import pyheclib
import pandas as pd
import numpy as np
import os
import time
class DSSFile:
    #DSS missing conventions
    MISSING_VALUE=-901.0
    MISSING_RECORD=-902.0
    FREQ_EPART_MAP = {
        pd.tseries.offsets.Minute(n=1):"1MIN",
        pd.tseries.offsets.Minute(n=2):"2MIN",
        pd.tseries.offsets.Minute(n=3):"3MIN",
        pd.tseries.offsets.Minute(n=4):"4MIN",
        pd.tseries.offsets.Minute(n=5):"5MIN",
        pd.tseries.offsets.Minute(n=10):"10MIN",
        pd.tseries.offsets.Minute(n=15):"15MIN",
        pd.tseries.offsets.Minute(n=20):"20MIN",
        pd.tseries.offsets.Minute(n=30):"30MIN",
        pd.tseries.offsets.Hour(n=1):"1HOUR",
        pd.tseries.offsets.Hour(n=2):"2HOUR",
        pd.tseries.offsets.Hour(n=3):"3HOUR",
        pd.tseries.offsets.Hour(n=4):"4HOUR",
        pd.tseries.offsets.Hour(n=6):"6HOUR",
        pd.tseries.offsets.Hour(n=8):"8HOUR",
        pd.tseries.offsets.Hour(n=12):"12HOUR",
        pd.tseries.offsets.Day(n=1):"1DAY",
        pd.tseries.offsets.Week(n=1):"1WEEK",
        pd.tseries.offsets.MonthEnd(n=1):"1MON",
        pd.tseries.offsets.YearEnd(n=1):"1YEAR"
    }
    EPART_FREQ_MAP={v: k for k, v in FREQ_EPART_MAP.items()}
    #
    def __init__(self,fname):
        self.ifltab=pyheclib.intArray(600)
        self.istat=0
        self.fname=fname
        self.isopen=False
        self.open()
    def __del__(self):
        self.close()
    def open(self):
        """
        Open DSS file
        """
        if (self.isopen): return
        self.istat=pyheclib.hec_zopen(self.ifltab,self.fname)
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
        opened_already= self.isopen
        try:
            if not opened_already: self.open()
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
            if not opened_already: self.close()
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
        if len(lines) < 9:
            print("Warning: catalog is empty! for filename: ",fdname)
            return None
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
        return pdf.apply(func=lambda x: '/'+('/'.join(list(x.values)))+'/',axis=1).values.tolist()
    def num_values_in_interval(self,sdstr,edstr,istr):
        """
        Get number of values in interval istr, using the start date and end date
        string
        """
        if istr.find('MON') >= 0: # less number of estimates will lead to overestimating values
            td=pd.to_timedelta(int(istr[:istr.find('MON')]),'M')
        elif istr.find('YEAR') >= 0:
            td=pd.to_timedelta(int(istr[:istr.find('YEAR')]),'Y')
        else:
            td=pd.to_timedelta(istr)
        return int((pd.to_datetime(edstr)-pd.to_datetime(sdstr))/td)+1
    def julian_day(self, date):
        """
        get julian day for the date. (count of days since beginning of year)
        """
        return date.dayofyear
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
    def _pad_to_end_of_block(self, endDateStr, interval):
        if interval.find('MON') >=0 or interval.find('YEAR') >=0:
            buffer=pd.DateOffset(years=10)
        elif interval.find('DAY') >=0 :
            buffer=pd.DateOffset(years=1)
        elif interval.find('HOUR') >=0 or interval.find('MIN') >= 0:
            buffer = pd.DateOffset(months=1)
        else:
            buffer=pd.DateOffset(days=1)
        return (pd.to_datetime(endDateStr) + buffer).strftime('%d%b%Y').upper()
    def read_rts(self,pathname,startDateStr=None, endDateStr=None):
        """
        read regular time series for pathname.
        if pathname D part contains a time window (START DATE "-" END DATE) and
        either start or end date is None it uses that to define start and end date
        """
        opened_already=self.isopen
        try:
            if not opened_already: self.open()
            interval = self.parse_pathname_epart(pathname)
            trim_first=False
            trim_last=False
            if startDateStr is None or endDateStr is None:
                twstr=pathname.split("/")[4]
                if twstr.find("-") < 0 :
                    raise Exception("No start date or end date and twstr is "+twstr)
                sdate,edate=twstr.split("-")
                if startDateStr is None:
                    trim_first=True
                    startDateStr=sdate.strip()
                if endDateStr is None:
                    trim_last=True
                    endDateStr=edate.strip()
                    endDateStr=self._pad_to_end_of_block(endDateStr,interval)
            nvals = self.num_values_in_interval(startDateStr, endDateStr, interval)
            sdate = pd.to_datetime(startDateStr)
            cdate = sdate.date().strftime('%d%b%Y').upper()
            ctime = ''.join(sdate.time().isoformat().split(':')[:2])
            dvalues = np.zeros(nvals,'d') # PERF: could be np.empty if all initialized
            nvals,cunits,ctype,iofset,istat=pyheclib.hec_zrrtsxd(self.ifltab, pathname, cdate, ctime,
                dvalues)
            #FIXME: raise appropriate exception for istat value
            #FIXME: deal with non-zero iofset
            freqoffset=DSSFile.EPART_FREQ_MAP[interval]
            if ctype == 'INST-VAL':
                dindex=pd.date_range(startDateStr,periods=nvals,freq=freqoffset)
            else:
                dindex=pd.period_range(startDateStr,periods=nvals,freq=freqoffset)
            df1=pd.DataFrame(data=dvalues,index=dindex,columns=[pathname])
            df1.replace([DSSFile.MISSING_VALUE,DSSFile.MISSING_RECORD],[np.nan,np.nan],inplace=True)
            if trim_first or trim_last:
                if trim_first:
                    first_index=df1.first_valid_index()
                else:
                    first_index=0
                if trim_last:
                    last_index = df1.last_valid_index()
                else:
                    last_index=None
                df1 = df1[first_index:last_index]
            else:
                df1 = df1
            return df1,cunits.strip(),ctype.strip()
        finally:
            if not opened_already: self.close()
    def write_rts(self, pathname, df, cunits, ctype):
        """
        write time series to this DSS file with the given pathname.
        The time series is passed in as a pandas DataFrame
        and associated units and types of length no greater than 8.
        """
        parts=pathname.split('/')
        parts[5]=DSSFile.FREQ_EPART_MAP[df.index.freq]
        pathname="/".join(parts)
        istat=pyheclib.hec_zsrtsxd(self.ifltab, pathname,
            df.index[0].strftime("%d%b%Y").upper(), df.index[0].strftime("%H%M"),
            df[0].values, cunits[:8], ctype[:8])
        #FIXME: raise exception with appropriate message for istat values
        return istat
    def _number_between(startDateStr, endDateStr, delta=pd.to_timedelta(1,'Y')):
        return (pd.to_datetime(endDateStr)-pd.to_datetime(startDateStr))/delta
    def _get_timedelta_unit(epart):
        if 'YEAR' in epart:
            return 'Y'
        elif 'MON' in epart:
            return 'M'
        elif 'WEEK' in epart:
            return 'W'
        elif 'DAY' in epart:
            return 'D'
        elif 'HOUR' in epart:
            return 'H'
        elif 'MIN' in epart:
            return 'm'
        else:
            raise Exception("Unknown epart to time delta conversion for epart=%s"%epart)
    def read_its(self, pathname, guess_vals_per_block=10000):
        """
        reads the entire irregular time series record. The timewindow is derived
        from the D-PART of the pathname so make sure to read that from the catalog
        before calling this function
        """
        parts=pathname.split('/')
        epart=parts[5]
        tw=list(map(lambda x: x.strip(),parts[4].split('-')))
        startDateStr=tw[0]
        endDateStr=self._pad_to_end_of_block(tw[1],epart)
        juls,istat=pyheclib.hec_datjul(startDateStr)
        jule,istat=pyheclib.hec_datjul(endDateStr)
        ietime=istime=0
        # guess how many values to be read based on e part approximation
        ktvals=DSSFile._number_between(startDateStr, endDateStr,
            pd.to_timedelta(1,unit=DSSFile._get_timedelta_unit(epart)))
        ktvals=guess_vals_per_block*int(ktvals)
        kdvals=ktvals
        itimes = np.zeros(ktvals,'i')
        dvalues = np.zeros(kdvals,'d')
        inflag = 0; # Retrieve both values preceding and following time window in addtion to time window
        nvals, ibdate, cunits, ctype, istat = pyheclib.hec_zritsxd(self.ifltab, pathname, juls, istime, jule, ietime, itimes, dvalues, inflag)
        if nvals == ktvals:
            raise Exception("More values than guessed! %d. Call with guess_vals_per_block > 10000 "%ktvals)
        base_date=pd.to_datetime('31DEC1899')+pd.to_timedelta(ibdate,'D')
        df=pd.DataFrame(dvalues[:nvals],index=pd.to_timedelta(itimes[:nvals],unit='m')+base_date,columns=[pathname])
        return df, cunits.strip(), ctype.strip()
        #return nvals, dvalues, itimes, base_date, cunits, ctype
    def write_its(self, pathname, df, cunits, ctype):
        pass
