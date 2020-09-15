from . import pyheclib
import pandas as pd
import numpy as np
import os
import time
import warnings
import logging
from datetime import datetime, timedelta
from calendar import monthrange
from dateutil.parser import parse
# some static functions

DATE_FMT_STR = '%d%b%Y'
_USE_CONDENSED=False

def set_message_level(level):
    """
    set the verbosity level of the HEC-DSS library
    level ranges from "bort" only (level 0) to "internal" (level >10)
    """
    pyheclib.hec_zset('MLEVEL', '', level)


def set_program_name(program_name):
    """
    sets the name of the program (upto 6 chars long) to store with data
    """
    name = program_name[:min(6, len(program_name))]
    pyheclib.hec_zset('PROGRAM', name, 0)


def get_version(fname):
    """
    Get version of DSS File
    returns a tuple of string version of 4 characters and integer version
    """
    return pyheclib.hec_zfver(fname)

def get_rts(filename, pathname):
    """
    Gets regular time series matching the pathname from the filename.
    Opens and reads pathname from filename and then closes it (slightly inefficient)

    Parameters
    ----------

    filename: a path to DSS file
    pathname: a string of the form /A/B/C/D/E/F that is parsed to match all parts except D
    which if not blank is used to determine the time window to retrieve
    D should be specified in the format of ddMMMYYYY HHmm - ddMMMYYYY HHmm

    Returns
    -------

    a list of tuple (pandas DataFrame, units, period type) for timeseries found or an empty list

    Notes
    -----
    Assumes that all matching are Regular time series ( as opposed to Irregular, See DSS terminolog)

    Examples
    --------

    Get time series based on a part of pathname, e.g.

    >>> pyhecdss.get_rts('test1.dss', '//SIN/////')
    [(rts,units,type),...]

    """
    dssh=DSSFile(filename)
    dfcat=dssh.read_catalog()
    try:
        pp=pathname.split('/')
        cond=True
        for p,n in zip(pp[1:4]+pp[5:7],['A','B','C','E','F']):
            if len(p)>0:
                cond = cond & (dfcat[n]==p)
        plist=dssh.get_pathnames(dfcat[cond])
        twstr = str.strip(pp[4])
        startDateStr=endDateStr=None
        if len(twstr) > 0:
            if str.find(twstr,'-') >= 0:
                startDateStr, endDateStr = list(map(lambda x: None if x == '' else x, map(str.strip,str.split(twstr,'-'))))
            else:
                startDateStr=twstr
        return [dssh.read_rts(p,startDateStr, endDateStr) for p in plist]
    finally:
        dssh.close()
    return []

def get_matching_rts(filename, pathname=None, path_parts=None):
    '''Opens the DSS file and reads matching pathname or path parts
    
    Args:

    :param filename: DSS filename containing data
    :param pathname: The DSS pathname A-F parts like string /A/B/C/D/E/F/
     where A-F is either blank implying match all or a regular expression to be matched
    or
    :param pathparts: if A-F regular expression contains the "/" character use the path_parts array instead
    
    *One of pathname or pathparts must be specified*

    :returns: an array of tuples of ( data as dataframe, units as string, type as string one of INST-VAL, PER-VAL)
    '''
    dssh=DSSFile(filename)
    dfcat=dssh.read_catalog()
    try:
        pp=pathname.split('/')
        cond=True
        for p,n in zip(pp[1:4]+pp[5:7],['A','B','C','E','F']):
            if len(p)>0:
                cond = cond & (dfcat[n].str.match(p))
        plist=dssh.get_pathnames(dfcat[cond])
        twstr = str.strip(pp[4])
        startDateStr=endDateStr=None
        if len(twstr) > 0:
            if str.find(twstr,'-') >= 0:
                startDateStr, endDateStr = list(map(lambda x: None if x == '' else x, map(str.strip,str.split(twstr,'-'))))
            else:
                startDateStr=twstr
        return [dssh.read_rts(p,startDateStr, endDateStr) for p in plist]
    finally:
        dssh.close()
    return []

class DSSFile:
    # DSS missing conventions
    MISSING_VALUE = -901.0
    MISSING_RECORD = -902.0
    #
    FREQ_NAME_MAP={"T":"MIN","H":"HOUR","D":"DAY","W":"WEEK","M":"MON","A-DEC":"YEAR"}
    #
    """
    vectorized version of timedelta
    """
    timedelta_minutes=np.vectorize(lambda x: timedelta(minutes=int(x)))


    def __init__(self, fname):
        self.isopen = False
        self._check_dir_exists(fname)
        self.ifltab = pyheclib.intArray(600)
        self.istat = 0
        self.fname = fname
        self.open()

    def __del__(self):
        self.close()

    def _check_dir_exists(self, fname):
        dname = os.path.dirname(fname)
        if dname == '' or os.path.exists(dname):
            return
        else:
            raise FileNotFoundError(
                "Attempt to create file: %s in non-existent directory: %s " % (fname, dname))

    def open(self):
        """
        Open DSS file
        """
        if (self.isopen):
            return
        self.istat = pyheclib.hec_zopen(self.ifltab, self.fname)
        self.isopen = True

    def close(self):
        """
        Close DSS File
        """
        # FIXME: remove all created arrays and pointers
        if (self.isopen):
            pyheclib.zclose_(self.ifltab)
            self.isopen = False

    def get_version(self):
        """
        Get version of DSS File
        returns a tuple of string version of 4 characters and integer version
        """
        # needs to be done on a closed file
        if (self.isopen):
            self.close()
        return pyheclib.hec_zfver(self.fname)

    def catalog(self):
        """
        Catalog DSS Files
        """
        opened_already = self.isopen
        try:
            if not opened_already:
                self.open()
            icunit = pyheclib.new_intp()  # unit (fortran) for catalog
            pyheclib.intp_assign(icunit, 12)
            fcname = self.fname[:self.fname.rfind(".")]+".dsc"
            pyheclib.fortranopen_(icunit, fcname, len(fcname))
            icdunit = pyheclib.new_intp()  # unit (fortran) for condensed catalog
            fdname = self.fname[:self.fname.rfind(".")]+".dsd"
            pyheclib.intp_assign(icdunit, 13)
            pyheclib.fortranopen_(icdunit, fdname, len(fdname))
            inunit = pyheclib.new_intp()
            # new catalog, if non-zero no cataloging
            pyheclib.intp_assign(inunit, 0)
            cinstr = ""  # catalog instructions : None = ""
            labrev = pyheclib.new_intp()
            pyheclib.intp_assign(labrev, 0)  # 0 is unabbreviated.
            ldsort = pyheclib.new_intp()
            pyheclib.intp_assign(ldsort, 1)  # 1 is sorted
            lcdcat = pyheclib.new_intp()  # output if condensed created
            nrecs = pyheclib.new_intp()  # number of records cataloged
            pyheclib.zcat_(self.ifltab, icunit, icdunit, inunit, cinstr,
                           labrev, ldsort, lcdcat, nrecs, len(cinstr))
            return pyheclib.intp_value(nrecs)
        except:
            #warnings.warn("Exception occurred while catalogging")
            pass
        finally:
            pyheclib.fortranflush_(icunit)
            pyheclib.fortranclose_(icunit)
            pyheclib.fortranflush_(icdunit)
            pyheclib.fortranclose_(icdunit)
            pyheclib.fortranflush_(inunit)
            pyheclib.fortranclose_(inunit)
            if not opened_already:
                self.close()
    
    def _read_catalog_dsd(self, fdname):
        '''
        read condensed catalog from fname into a data frame
        '''
        with open(fdname, 'r') as fd:
            lines = fd.readlines()
        columns = ['Tag', 'A Part', 'B Part',
                   'C Part', 'F Part', 'E Part', 'D Part']
        if len(lines) < 9:
            logging.warn("catalog is empty! for filename: ", fdname)
            return None
        colline = lines[7]
        column_indices = []
        for c in columns:
            column_indices.append(colline.find(c))
        a = np.empty([len(columns), len(lines)-9], dtype='U132')
        ilx = 0
        for line in lines[9:]:
            cix = 0
            isx = column_indices[0]
            for iex in column_indices[1:]:
                s = line[isx:iex].strip()
                if s.startswith("-"):
                    s = a[cix, ilx-1]
                a[cix, ilx] = s
                cix = cix+1
                isx = iex
            s = line[isx:].strip()
            a[cix, ilx] = s
            ilx = ilx+1
        df = pd.DataFrame(a.transpose(), columns=list('TABCFED'))
        return df

    def _read_catalog_dsc(self, fcname):
        '''
        read full catalog from fc name and create condensed catalog on the fly
        returns data frame 
        '''
        df=pd.read_fwf(fcname,skiprows=8,colspecs=[(0,8),(8,15),(15,500)])
        df=df.dropna()
        df[list('ABCDEF')]=df['Record Pathname'].str.split('/',expand=True).iloc[:,1:7]
        dfg=df.groupby(['A','B','C','F','E'])
        dfmin,dfmax=dfg.min(),dfg.max()
        tagmax='T'+str(dfmax.Tag.str[1:].astype('int').max())
        dfc=dfmin['D']+'-'+dfmax['D']
        dfc=dfc.reset_index()
        dfc.insert(0,'T',tagmax)
        return dfc
    
    def _check_condensed_catalog_file_and_recatalog(self, condensed=True):
        if condensed:
            ext='.dsd'
        else:
            ext='.dsc'
        fdname = self.fname[:self.fname.rfind(".")]+ext
        if not os.path.exists(fdname):
            logging.debug("NO CATALOG FOUND: Generating...")
            self.catalog()
        else:
            if os.path.exists(self.fname):
                ftime = pd.to_datetime(time.ctime(
                    os.path.getmtime(self.fname)))
                fdtime = pd.to_datetime(time.ctime(os.path.getmtime(fdname)))
                if ftime > fdtime:
                    logging.debug("CATALOG FILE OLD: Generating...")
                    self.catalog()
            else:
                logging.debug("No DSS File found. Using catalog file as is")
        #
        return fdname

    def read_catalog(self):
        """
        Reads .dsd (condensed catalog) for the given dss file.
        Will run catalog if it doesn't exist or is out of date
        """
        fdname=self._check_condensed_catalog_file_and_recatalog(condensed=_USE_CONDENSED)
        if _USE_CONDENSED:
            df=self._read_catalog_dsd(fdname)
        else:
            df=self._read_catalog_dsc(fdname)
        return df

    def get_pathnames(self, catalog_dataframe=None):
        """
        converts a catalog data frame into pathnames
        If catalog_dataframe is None then reads catalog to populate it

        returns a list of pathnames (condensed version, i.e. D part is time window)
        /A PART/B PART/C PART/DPART (START DATE "-" END DATE)/E PART/F PART/
        """
        if catalog_dataframe is None:
            catalog_dataframe = self.read_catalog()
        pdf = catalog_dataframe.iloc[:, [1, 2, 3, 6, 5, 4]]
        return pdf.apply(func=lambda x: '/'+('/'.join(list(x.values)))+'/', axis=1).values.tolist()

    def num_values_in_interval(self, sdstr, edstr, istr):
        """
        Get number of values in interval istr, using the start date and end date
        string
        """
        td=DSSFile._get_timedelta_for_interval(istr)
        return int((parse(edstr)-parse(sdstr))/td)+1

    def julian_day(self, date):
        """
        get julian day for the date. (count of days since beginning of year)
        """
        return date.dayofyear

    def m2ihm(self, minute):
        """
        24 hour style from mins
        """
        ihr = minute/60
        imin = minute-(ihr*60)
        itime = ihr*100+imin
        return itime

    def parse_pathname_epart(self, pathname):
        return pathname.split('/')[1:7][4]

    def _number_between(startDateStr, endDateStr, delta=timedelta(days=1)):
        """
        This is just a guess at number of values to be read so going over is ok.
        """
        return round((parse(endDateStr)-parse(startDateStr))/delta+1)

    def _get_timedelta_for_interval(interval):
        """
        get minimum timedelta for interval defined by string. e.g. for month it is 28 days (minimum)
        """
        if interval.find('MON') >= 0:  # less number of estimates will lead to overestimating values
            td = timedelta(days=28)
        elif interval.find('YEAR') >= 0:
            td = timedelta(days=365)
        else:
            td = timedelta(seconds=DSSFile.get_freq_from_epart(interval).nanos/1e9)
        return td

    def _pad_to_end_of_block(self, endDateStr, interval):
        edate=parse(endDateStr)
        if interval.find('MON') >= 0 or interval.find('YEAR') >= 0:
            edate=datetime((edate.year//10+1)*10,1,1)
        elif interval.find('DAY') >= 0:
            edate=datetime(edate.year+1,1,1)
        elif interval.find('HOUR') >= 0 or interval.find('MIN') >= 0:
            if edate.month == 12:
                edate=datetime(edate.year+1,1,1)
            else:
                edate=datetime(edate.year,edate.month+1,1)
        else:
            edate = edate+timedelta(days=1)
        return edate.strftime(DATE_FMT_STR).upper()

    def _get_istat_for_zrrtsxd(self, istat):
        """
        C        ISTAT:   Integer status parameter, indicating the
        C                 successfullness of the retrieval.
        C                 ISTAT = 0  All ok.
        C                 ISTAT = 1  Some missing data (still ok)
        C                 ISTAT = 2  Missing data blocks, but some data found
        C                 ISTAT = 3  Combination of 1 and 2 (some data found)
        C                 ISTAT = 4  No data found, although a pathname was read
        C                 ISTAT = 5  No pathname(s) found
        C                 ISTAT > 9  Illegal call to ZRRTS
        """
        if istat == 0:
            return "All good"
        msg = "ISTAT: %d --> " % istat
        if istat == 1:
            msg = msg + "Some missing data (still ok)"
        elif istat == 2:
            msg = msg + "Missing data blocks, but some data found"
        elif istat == 3:
            msg = msg + "Combination of 1 and 2 (some data found)"
        elif istat == 4:
            msg = msg + "No data found, although a pathname was read"
        elif istat == 5:
            msg = msg + "No pathname(s) found"
        elif istat > 9:
            msg = msg + "Illegal call to ZRRTS"
        return msg

    def _respond_to_istat_state(self, istat):
        if istat == 0:
            # everything is ok
            pass
        elif istat == 1 or istat == 2 or istat == 3:
            logging.debug(
                "Some data or data blocks are missing [istat=" + str(istat) + "]", RuntimeWarning)
        elif istat == 4:
            logging.debug(
                "Found file but failed to load any data", RuntimeWarning)
        elif istat == 5:
            logging.debug("Path not found")
        elif istat > 9:
            logging.debug("Illegal internal call")
    
    def _parse_times(self, pathname, startDateStr=None, endDateStr=None):
        '''
        parse times based on pathname or startDateStr and endDateStr
        start date and end dates may be padded to include a larger interval
        '''
        interval = self.parse_pathname_epart(pathname)
        if startDateStr is None or endDateStr is None:
            twstr = pathname.split("/")[4]
            if twstr.find("-") < 0:
                if len(twstr.strip()) == 0:
                    raise Exception(
                        "No start date or end date and twstr is "+twstr)
                sdate = edate = twstr
            else:
                sdate, edate = twstr.replace("*","").split("-")
            if startDateStr is None:
                startDateStr = sdate.strip()
            if endDateStr is None:
                endDateStr = edate.strip()
                endDateStr = self._pad_to_end_of_block(
                    endDateStr, interval)
        return startDateStr, endDateStr

    def read_rts(self, pathname, startDateStr=None, endDateStr=None):
        """
        read regular time series for pathname.
        if pathname D part contains a time window (START DATE "-" END DATE) and
        either start or end date is None it uses that to define start and end date
        """
        opened_already = self.isopen
        try:
            if not opened_already:
                self.open()
            interval = self.parse_pathname_epart(pathname)
            trim_first = startDateStr is None
            trim_last = endDateStr is None
            startDateStr, endDateStr = self._parse_times(pathname, startDateStr, endDateStr)
            nvals = self.num_values_in_interval(startDateStr, endDateStr, interval)
            sdate = parse(startDateStr)
            cdate = sdate.date().strftime('%d%b%Y').upper()
            ctime = ''.join(sdate.time().isoformat().split(':')[:2])
            # PERF: could be np.empty if all initialized
            dvalues = np.zeros(nvals, 'd')
            nvals, cunits, ctype, iofset, istat = pyheclib.hec_zrrtsxd(self.ifltab, pathname, cdate, ctime,
                                                                       dvalues)
            # FIXME: raise appropriate exception for istat value
            # if istat != 0:
            #    raise Exception(self._get_istat_for_zrrtsxd(istat))
            self._respond_to_istat_state(istat)

            # FIXME: deal with non-zero iofset for period data,i.e. else part of if stmt below
            freqoffset = DSSFile.get_freq_from_epart(interval)
            if ctype.startswith('INST'):
                startDateWithOffset=parse(startDateStr)
                if iofset !=0:
                    startDateWithOffset=parse(startDateStr)-freqoffset+timedelta(minutes=iofset)
                dindex = pd.date_range(
                    startDateWithOffset, periods=nvals, freq=freqoffset)
            else:
                sp = pd.Period(startDateStr, freq=freqoffset) - \
                    pd.tseries.frequencies.to_offset(freqoffset)
                dindex = pd.period_range(sp, periods=nvals, freq=freqoffset)
            df1 = pd.DataFrame(data=dvalues, index=dindex, columns=[pathname])
            # cleanup missing values --> NAN, trim dataset and units and period type strings
            df1.replace([DSSFile.MISSING_VALUE, DSSFile.MISSING_RECORD], [
                        np.nan, np.nan], inplace=True)
            if trim_first or trim_last:
                if trim_first:
                    first_index = df1.first_valid_index()
                else:
                    first_index = df1.index[0]
                if trim_last:
                    last_index = df1.last_valid_index()
                else:
                    last_index = df1.index[-1]
                df1 = df1[first_index:last_index]
            else:
                df1 = df1
            return df1, cunits.strip(), ctype.strip()
        finally:
            if not opened_already:
                self.close()

    def get_epart_from_freq(freq):
        return "%d%s"%(freq.n,DSSFile.FREQ_NAME_MAP[freq.name])

    def get_freq_from_epart(epart):
        if epart.find('MON') >= 0: 
            td = pd.offsets.MonthEnd(n=int(str.split(epart,'MON')[0]))
        elif epart.find('DAY') >=0:
            td = pd.offsets.Day(n=int(str.split(epart,'DAY')[0]))
        elif epart.find('HOUR') >=0:
            td = pd.offsets.Hour(n=int(str.split(epart,'HOUR')[0]))
        elif epart.find('MIN') >=0:
            td = pd.offsets.Minute(n=int(str.split(epart,'MIN')[0]))
        elif epart.find('YEAR') >= 0:
            td = pd.offsets.YearEnd(n=int(str.split(epart,'YEAR')[0]))
        elif epart.find('WEEK') >=0:
            td = pd.offsets.Minute(n=int(str.split(epart,'MIN')[0]))
        else:
            raise RuntimeError('Could not understand interval: ',epart)
        return td
  

    def write_rts(self, pathname, df, cunits, ctype):
        """
        write time series to this DSS file with the given pathname.
        The time series is passed in as a pandas DataFrame
        and associated units and types of length no greater than 8.
        """
        parts = pathname.split('/')
        parts[5] = DSSFile.get_epart_from_freq(df.index.freq)
        pathname = "/".join(parts)
        if isinstance(df.index[0], pd.Period):
            sp = df.index[0].to_timestamp(how='end')
        else:
            sp = df.index[0]
        istat = pyheclib.hec_zsrtsxd(self.ifltab, pathname,
                                     sp.strftime("%d%b%Y").upper(
                                     ), sp.round(freq='T').strftime("%H%M"),
                                     df.iloc[:, 0].values, cunits[:8], ctype[:8])
        self._respond_to_istat_state(istat)

    def read_its(self, pathname, startDateStr=None, endDateStr=None, guess_vals_per_block=10000):
        """
        reads the entire irregular time series record. The timewindow is derived
        from the D-PART of the pathname so make sure to read that from the catalog
        before calling this function
        """
        epart = self.parse_pathname_epart(pathname)
        startDateStr,endDateStr=self._parse_times(pathname, startDateStr, endDateStr)
        juls, istat = pyheclib.hec_datjul(startDateStr)
        jule, istat = pyheclib.hec_datjul(endDateStr)
        ietime = istime = 0
        # guess how many values to be read based on e part approximation
        ktvals = DSSFile._number_between(startDateStr, endDateStr, DSSFile._get_timedelta_for_interval(epart))
        ktvals = guess_vals_per_block*int(ktvals)
        kdvals = ktvals
        itimes = np.zeros(ktvals, 'i')
        dvalues = np.zeros(kdvals, 'd')
        inflag = 0  # Retrieve both values preceding and following time window in addtion to time window
        nvals, ibdate, cunits, ctype, istat = pyheclib.hec_zritsxd(
            self.ifltab, pathname, juls, istime, jule, ietime, itimes, dvalues, inflag)
        self._respond_to_istat_state(istat)
        if nvals == ktvals:
            raise Exception(
                "More values than guessed! %d. Call with guess_vals_per_block > 10000 " % ktvals)
        base_date = parse('31DEC1899')+timedelta(days=ibdate)
        df = pd.DataFrame(dvalues[:nvals], index=base_date+DSSFile.timedelta_minutes(itimes[:nvals]), columns=[pathname])
        return df, cunits.strip(), ctype.strip()
        # return nvals, dvalues, itimes, base_date, cunits, ctype

    def write_its(self, pathname, df, cunits, ctype, interval=None):
        """
        write irregular time series to the pathname.

        The timewindow part of the pathname (D PART) is used to establish the base julian date
        for storage of the time values (minutes relative to that base julian date)

        The interval is the block size to store irregular time series for efficient access
        interval values should be "IR-YEAR", "IR-MONTH" or "IR-DAY"

        Uses the provided pandas.DataFrame df index (time) and values
        and also stores the units (cunits) and type (ctype)
        """
        parts = pathname.split('/')
        # parts[5]=DSSFile.FREQ_EPART_MAP[df.index.freq]
        if interval:
            parts[5] = interval
        else:
            if len(parts[5]) == 0:
                raise Exception(
                    "Specify interval = IR-YEAR or IR-MONTH or IR-DAY or provide it the pathname (5th position)")
        epart = parts[5]
        if len(parts[4]) == 0:
            startDateStr = (
                df.index[0]-pd.offsets.YearBegin(1)).strftime('%d%b%Y').upper()
            endDateStr = (df.index[-1]+pd.offsets.YearBegin(0)
                          ).strftime('%d%b%Y').upper()
            parts[4] = startDateStr + " - " + endDateStr
        else:
            tw = list(map(lambda x: x.strip(), parts[4].split('-')))
            startDateStr = tw[0]
            endDateStr = tw[1]  # self._pad_to_end_of_block(tw[1],epart)
        juls, istat = pyheclib.hec_datjul(startDateStr)
        jule, istat = pyheclib.hec_datjul(endDateStr)
        ietime = istime = 0
        pathname = "/".join(parts)
        itimes = df.index-parse(startDateStr)
        itimes = itimes.total_seconds()/60  # time in minutes since base date juls
        itimes = itimes.values.astype('i')  # conver to integer numpy
        inflag = 1  # replace data (merging should be done in memory)
        istat = pyheclib.hec_zsitsxd(self.ifltab, pathname,
                                     itimes, df.iloc[:, 0].values, juls, cunits, ctype, inflag)
        self._respond_to_istat_state(istat)
        # return istat
