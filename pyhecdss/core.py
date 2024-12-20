import collections
from . import _pyheclib as pyheclib
import pandas as pd
import numpy as np
import os
import re
import time
import warnings
import logging
from datetime import datetime, timedelta
from calendar import monthrange
from dateutil.parser import parse

# some static functions

DATE_FMT_STR = "%d%b%Y"
_USE_CONDENSED = False


def set_message_level(level):
    """
    set the verbosity level of the HEC-DSS library
    level ranges from "bort" only (level 0) to "internal" (level >10)
    """
    pyheclib.hec_zset("MLEVEL", "", level)


def set_program_name(program_name):
    """
    sets the name of the program (upto 6 chars long) to store with data
    """
    name = program_name[: min(6, len(program_name))]
    pyheclib.hec_zset("PROGRAM", name, 0)


def get_version(fname):
    """
    Get version of DSS File
    returns a tuple of string version of 4 characters and integer version
    """
    return pyheclib.hec_zfver(fname)


def get_start_end_dates(twstr, sep="-"):
    """
    Get the start and end date (as strings of format ddMMMyyyy,e.g. 01JAN1991) from timewindow string
    The start and end times must be separated by sep (default = '-') and can be in any format that works with
    pandas to_datetime (see link below)

    The returned start and end date are rounded down and up (respectively) to the day

    Args:
        twstr (str): timewindow as string of the form that can be parsed by pd.to_datetime [https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html]
    """
    s, e = [pd.to_datetime(str.strip(d)) for d in str.split(twstr, sep)]
    return (
        s.floor("D").strftime("%d%b%Y").upper(),
        e.ceil("D").strftime("%d%b%Y").upper(),
    )


def get_ts(filename, *paths):
    """
    Gets regular time series matching the pathname(s) from the filename.
    Opens and reads pathname(s) from filename and then closes it (slightly inefficient)

    Parameters
    ----------

    filename: a path to DSS file
    pathname(s): one or more strings of the form /A/B/C/D/E/F that is parsed to match all parts except D
    which if not blank is used to determine the time window to retrieve
    D should be specified in the format of ddMMMYYYY HHmm - ddMMMYYYY HHmm

    Returns
    -------

    a generator of named tuples DSSData(data=pandas DataFrame, units=units, period_type=period type) for timeseries found or an empty list

    Notes
    -----
    Assumes that all matching are Regular time series ( as opposed to Irregular, See DSS terminolog)

    Examples
    --------

    Get time series based on a part of pathname, e.g.

    >>> pyhecdss.get_rts('test1.dss', '//SIN/////', '//COS/////')
    [(rts,units,type),...]

    """
    with DSSFile(filename) as dssh:
        dfcat = dssh.read_catalog()
        for pathname in paths:
            if pathname:
                pathname = pathname.upper()
            pp = pathname.split("/")
            cond = True
            for p, n in zip(pp[1:4] + pp[5:7], ["A", "B", "C", "E", "F"]):
                if len(p) > 0:
                    cond = cond & (dfcat[n] == p)
            plist = dssh.get_pathnames(dfcat[cond])
            twstr = str.strip(pp[4])
            startDateStr = endDateStr = None
            if len(twstr) > 0:
                try:
                    startDateStr, endDateStr = get_start_end_dates(twstr)
                except:
                    startDateStr, endDateStr = None, None
            for p in plist:
                if p.split("/")[5].startswith("IR-"):
                    yield dssh.read_its(p, startDateStr, endDateStr)
                else:
                    yield dssh.read_rts(p, startDateStr, endDateStr)


def get_matching_ts(filename, pathname=None, path_parts=None):
    """Opens the DSS file and reads matching pathname or path parts

    Args:

    :param filename: DSS filename containing data
    :param pathname: The DSS pathname A-F parts like string /A/B/C/D/E/F/
     where A-F is either blank implying match all or a regular expression to be matched
    or
    :param pathparts: if A-F regular expression contains the "/" character use the path_parts array instead

    *One of pathname or pathparts must be specified*

    :returns: an generator of named tuples of DSSData ( data as dataframe, units as string, type as string one of INST-VAL, PER-VAL)
    """
    with DSSFile(filename) as dssh:
        dfcat = dssh.read_catalog()
        if pathname:
            pathname = pathname.upper()
        pp = pathname.split("/")
        cond = dfcat["A"].str.match(".*")
        for p, n in zip(pp[1:4] + pp[5:7], ["A", "B", "C", "E", "F"]):
            if len(p) > 0:
                cond = cond & (dfcat[n].str.match(p))
        plist = dssh.get_pathnames(dfcat[cond])
        twstr = str.strip(pp[4])
        startDateStr = endDateStr = None
        if len(twstr) > 0:
            try:
                startDateStr, endDateStr = get_start_end_dates(twstr)
            except:
                startDateStr, endDateStr = None, None
        if len(plist) == 0:
            raise Exception(
                f"No pathname found in {filename} for {pathname} or {path_parts}"
            )
        for p in plist:
            if p.split("/")[5].startswith("IR-"):
                yield dssh.read_its(p, startDateStr, endDateStr)
            else:
                yield dssh.read_rts(p, startDateStr, endDateStr)


DSSData = collections.namedtuple(
    "DSSData", field_names=["data", "units", "period_type"]
)


class DSSFile:
    """
    Opens a HEC-DSS file for operations of read and write.
    The correct way of using is "with" statement:

    ```
    with DSSFile('myfile.dss') as dh:
        dfcat=dh.read_catalog()
    ```

    Raises:
        FileNotFoundError: If the path to the file is not found. Usually silently creats an empty file if missing

    Returns:
        DSSFile: an open DSS file handle
    """

    # DSS missing conventions
    MISSING_VALUE = -901.0
    MISSING_RECORD = -902.0
    #
    FREQ_NAME_MAP = {
        "min": "MIN",
        "h": "HOUR",
        "D": "DAY",
        "W": "WEEK",
        "M": "MON",
        "A-DEC": "YEAR",
    }
    #
    NAME_FREQ_MAP = {v: k for k, v in FREQ_NAME_MAP.items()}
    #
    EPART_PATTERN = re.compile(
        r"(?P<n>\d+)(?P<interval>M[O|I]N|YEAR|HOUR|DAY|WEEK)", re.UNICODE
    )
    #
    """
    vectorized version of timedelta
    """
    timedelta_minutes = np.vectorize(lambda x: timedelta(minutes=int(x)), otypes=["O"])

    def __init__(self, fname, create_new=False):
        """Opens a dssfile

        Args:
            fname (str): path to filename
            create_new (bool, optional): create_new if file doesn't exist. Defaults to False.
        """
        self.isopen = False
        self._check_dir_exists(fname)
        if not create_new:
            if not os.path.exists(fname) and not os.path.isfile(fname):
                raise Exception(
                    f"File path: {fname} does not exist! "
                    + "Use create_new=True if you want to create a new file"
                )
        self.ifltab = pyheclib.intArray(600)
        self.istat = 0
        self.fname = fname
        self.open()

    # defining __enter__ and __exit__ for use with "with" statements
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def _check_dir_exists(self, fname):
        dname = os.path.dirname(fname)
        if dname == "" or os.path.exists(dname):
            return
        else:
            raise FileNotFoundError(
                "Attempt to create file: %s in non-existent directory: %s "
                % (fname, dname)
            )

    def open(self):
        """
        Open DSS file
        """
        if self.isopen:
            return
        self.istat = pyheclib.hec_zopen(self.ifltab, self.fname)
        self.isopen = True

    def close(self):
        """
        Close DSS File
        """
        # FIXME: remove all created arrays and pointers
        if self.isopen:
            pyheclib.zclose_(self.ifltab)
            self.isopen = False

    def get_version(self):
        """
        Get version of DSS File
        returns a tuple of string version of 4 characters and integer version
        """
        # needs to be done on a closed file
        if self.isopen:
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
            fcname = self.fname[: self.fname.rfind(".")] + ".dsc"
            pyheclib.fortranopen_(icunit, fcname, len(fcname))
            icdunit = pyheclib.new_intp()  # unit (fortran) for condensed catalog
            fdname = self.fname[: self.fname.rfind(".")] + ".dsd"
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
            pyheclib.zcat_(
                self.ifltab,
                icunit,
                icdunit,
                inunit,
                cinstr,
                labrev,
                ldsort,
                lcdcat,
                nrecs,
                len(cinstr),
            )
            return pyheclib.intp_value(nrecs)
        except:
            # warnings.warn("Exception occurred while catalogging")
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

    @staticmethod
    def _read_catalog_dsd(fdname):
        """
        read condensed catalog from fname into a data frame
        """
        with open(fdname, "r") as fd:
            lines = fd.readlines()
        columns = ["Tag", "A Part", "B Part", "C Part", "F Part", "E Part", "D Part"]
        if len(lines) < 9:
            logging.warn("catalog is empty! for filename: ", fdname)
            return None
        colline = lines[7]
        column_indices = []
        for c in columns:
            column_indices.append(colline.find(c))
        a = np.empty([len(columns), len(lines) - 9], dtype="U132")
        ilx = 0
        for line in lines[9:]:
            cix = 0
            isx = column_indices[0]
            for iex in column_indices[1:]:
                s = line[isx:iex].strip()
                if s.startswith("-"):
                    s = a[cix, ilx - 1]
                a[cix, ilx] = s
                cix = cix + 1
                isx = iex
            s = line[isx:].strip()
            a[cix, ilx] = s
            ilx = ilx + 1
        df = pd.DataFrame(a.transpose(), columns=list("TABCFED"))
        return df

    @staticmethod
    def _read_catalog_dsc(fcname):
        """
        read full catalog from fc name and create condensed catalog on the fly
        returns data frame
        """
        df = pd.read_fwf(fcname, skiprows=8, colspecs=[(0, 8), (8, 15), (15, 500)])
        df = df.dropna(how="all", axis=0)  # drop empty lines
        df[list("ABCDEF")] = (
            df["Record Pathname"].str.split("/", expand=True).iloc[:, 1:7]
        )
        dfg = df.groupby(["A", "B", "C", "F", "E"])
        df.D = pd.to_datetime(df.D, format="%d%b%Y")
        dfmin, dfmax = dfg.min(), dfg.max()
        tagmax = "T" + str(
            dfmax.Tag.astype("str").str[1:].astype("int", errors="ignore").max()
        )
        dfc = (
            dfmin["D"].dt.strftime("%d%b%Y").str.upper()
            + " - "
            + dfmax["D"].dt.strftime("%d%b%Y").str.upper()
        )
        dfc = dfc.reset_index()
        dfc.insert(0, "T", tagmax)
        return dfc

    def _check_condensed_catalog_file_and_recatalog(self, condensed=True):
        """
        check if cataloging is needed to generate the catalog files (condensed or otherwise)

        returns name of catalog file and if it was regenerated (True) or not (False)
        """
        generated = False
        if condensed:
            ext = ".dsd"
        else:
            ext = ".dsc"
        fdname = self.fname[: self.fname.rfind(".")] + ext
        if not os.path.exists(fdname):
            logging.debug("NO CATALOG FOUND: Generating...")
            self.catalog()
            generated = True
        else:
            if os.path.exists(self.fname):
                ftime = pd.to_datetime(time.ctime(os.path.getmtime(self.fname)))
                fdtime = pd.to_datetime(time.ctime(os.path.getmtime(fdname)))
                if ftime > fdtime:
                    logging.debug("CATALOG FILE OLD: Generating...")
                    self.catalog()
                    generated = True
            else:
                logging.debug("No DSS File found. Using catalog file as is")
        #
        return fdname, generated

    def read_catalog(self):
        """
        Reads .dsd (condensed catalog) for the given dss file.
        Will run catalog if it doesn't exist or is out of date
        """
        fdname, generated = self._check_condensed_catalog_file_and_recatalog(
            condensed=_USE_CONDENSED
        )
        if _USE_CONDENSED:
            df = DSSFile._read_catalog_dsd(fdname)
        else:
            df = DSSFile._read_catalog_dsc(fdname)
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
        return pdf.apply(
            func=lambda x: "/" + ("/".join(list(x.values))) + "/", axis=1
        ).values.tolist()

    def num_values_in_interval(sdstr, edstr, istr):
        """
        Get number of values in interval istr, using the start date and end date
        string
        """
        td = DSSFile._get_timedelta_for_interval(istr)
        return int((parse(edstr) - parse(sdstr)) / td) + 1

    def julian_day(self, date):
        """
        get julian day for the date. (count of days since beginning of year)
        """
        return date.dayofyear

    def m2ihm(self, minute):
        """
        24 hour style from mins
        """
        ihr = minute / 60
        imin = minute - (ihr * 60)
        itime = ihr * 100 + imin
        return itime

    def parse_pathname_epart(self, pathname):
        return pathname.split("/")[1:7][4]

    def _number_between(startDateStr, endDateStr, delta=timedelta(days=1)):
        """
        This is just a guess at number of values to be read so going over is ok.
        """
        return round((parse(endDateStr) - parse(startDateStr)) / delta + 1)

    def _get_timedelta_for_interval(interval):
        """
        get minimum timedelta for interval defined by string. e.g. for month it is 28 days (minimum)
        """
        if (
            interval.find("MON") >= 0
        ):  # less number of estimates will lead to overestimating values
            td = timedelta(days=28)
        elif interval.find("YEAR") >= 0:
            td = timedelta(days=365)
        # TODO: Added to process IR-DAY and IR-DECADE, but this will make
        # the routine bypass `get_freq_from_epart` for regular DAY intervals.
        # Rewriting some of the logics here would be better for efficiency.
        elif interval.find("DAY") >= 0:
            td = timedelta(days=1)  # Assuming the maximum daily.
        elif interval.find("DECADE") >= 0:
            td = timedelta(days=365)  # Assuming it is close to YEARLY
        elif interval.find("DECADE") >= 0:
            td = timedelta(days=3650)
        else:
            td = timedelta(seconds=DSSFile.get_freq_from_epart(interval).nanos / 1e9)
        return td

    def _pad_to_end_of_block(self, endDateStr, interval):
        edate = parse(endDateStr)
        if interval.find("MON") >= 0 or interval.find("YEAR") >= 0:
            edate = datetime((edate.year // 10 + 1) * 10, 1, 1)
        elif interval.find("DAY") >= 0:
            edate = datetime(edate.year + 1, 1, 1)
        elif interval.find("HOUR") >= 0 or interval.find("MIN") >= 0:
            if edate.month == 12:
                edate = datetime(edate.year + 1, 1, 1)
            else:
                edate = datetime(edate.year, edate.month + 1, 1)
        else:
            edate = edate + timedelta(days=1)
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
                "Some data or data blocks are missing [istat=" + str(istat) + "]",
                RuntimeWarning,
            )
        elif istat == 4:
            logging.debug("Found file but failed to load any data", RuntimeWarning)
        elif istat == 5:
            logging.debug("Path not found")
        elif istat > 9:
            logging.debug("Illegal internal call")

    def _parse_times(self, pathname, startDateStr=None, endDateStr=None):
        """
        parse times based on pathname or startDateStr and endDateStr
        start date and end dates may be padded to include a larger interval
        """
        interval = self.parse_pathname_epart(pathname)
        if startDateStr is None or endDateStr is None:
            twstr = pathname.split("/")[4]
            if twstr.find("-") < 0:
                if len(twstr.strip()) == 0:
                    raise Exception("No start date or end date and twstr is " + twstr)
                sdate = edate = twstr
            else:
                sdate, edate = twstr.replace("*", "").split("-")
            if startDateStr is None:
                startDateStr = sdate.strip()
            if endDateStr is None:
                endDateStr = edate.strip()
                endDateStr = self._pad_to_end_of_block(endDateStr, interval)
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
            if pathname:
                pathname = pathname.upper()
            interval = self.parse_pathname_epart(pathname)
            trim_first = startDateStr is None
            trim_last = endDateStr is None
            startDateStr, endDateStr = self._parse_times(
                pathname, startDateStr, endDateStr
            )
            nvals = DSSFile.num_values_in_interval(startDateStr, endDateStr, interval)
            sdate = parse(startDateStr)
            cdate = sdate.date().strftime("%d%b%Y").upper()
            ctime = "".join(sdate.time().isoformat().split(":")[:2])
            # PERF: could be np.empty if all initialized
            dvalues = np.zeros(nvals, "d")
            nvals, cunits, ctype, iofset, istat = pyheclib.hec_zrrtsxd(
                self.ifltab, pathname, cdate, ctime, dvalues
            )
            # FIXME: raise appropriate exception for istat value
            # if istat != 0:
            #    raise Exception(self._get_istat_for_zrrtsxd(istat))
            self._respond_to_istat_state(istat)

            # FIXME: deal with non-zero iofset for period data,i.e. else part of if stmt below
            nfreq, freqstr = DSSFile.get_number_and_frequency_from_epart(interval)
            freqstr = "%d%s" % (nfreq, DSSFile.NAME_FREQ_MAP[freqstr])
            freqoffset = DSSFile.get_freq_from_epart(interval)
            if ctype.startswith("PER"):  # for period values, shift back 1
                # - pd.tseries.frequencies.to_offset(freqoffset)
                sp = pd.Period(startDateStr, freq=freqstr)
                dindex = pd.period_range(sp, periods=nvals, freq=freqstr).shift(-1)
            else:
                startDateWithOffset = parse(startDateStr)
                if (
                    iofset != 0
                ):  # offsets are always from the end of the period, e.g. for day, rewind by a day and then add offset
                    startDateWithOffset = (
                        parse(startDateStr) - freqoffset + timedelta(minutes=iofset)
                    )
                dindex = pd.date_range(
                    startDateWithOffset, periods=nvals, freq=freqoffset
                )
            df1 = pd.DataFrame(data=dvalues, index=dindex, columns=[pathname])
            # cleanup missing values --> NAN, trim dataset and units and period type strings
            df1.replace(
                [DSSFile.MISSING_VALUE, DSSFile.MISSING_RECORD],
                [np.nan, np.nan],
                inplace=True,
            )
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
            return DSSData(data=df1, units=cunits.strip(), period_type=ctype.strip())
        finally:
            if not opened_already:
                self.close()

    def get_epart_from_freq(freq):
        if freq.name == "ME":
            freq_name = "M"
        elif freq.name == "T":
            freq_name = "min"
        else:
            freq_name = freq.name
        return "%d%s" % (freq.n, DSSFile.FREQ_NAME_MAP[freq_name])

    def get_number_and_frequency_from_epart(epart):
        match = DSSFile.EPART_PATTERN.match(epart)
        return int(match["n"]), match["interval"]

    def get_freq_from_epart(epart):
        if epart.find("MON") >= 0:
            td = pd.offsets.MonthBegin(n=int(str.split(epart, "MON")[0]))
        elif epart.find("DAY") >= 0:
            td = pd.offsets.Day(n=int(str.split(epart, "DAY")[0]))
        elif epart.find("HOUR") >= 0:
            td = pd.offsets.Hour(n=int(str.split(epart, "HOUR")[0]))
        elif epart.find("MIN") >= 0:
            td = pd.offsets.Minute(n=int(str.split(epart, "MIN")[0]))
        elif epart.find("YEAR") >= 0:
            td = pd.offsets.YearBegin(n=int(str.split(epart, "YEAR")[0]))
        elif epart.find("WEEK") >= 0:
            td = pd.offsets.Week(n=int(str.split(epart, "WEEK")[0]))
        else:
            raise RuntimeError("Could not understand interval: ", epart)
        return td

    def write_rts(self, pathname, df, cunits, ctype):
        """
        write time series to this DSS file with the given pathname.
        The time series is passed in as a pandas DataFrame
        and associated units and types of length no greater than 8.
        """
        if pathname:
            pathname = pathname.upper()
        parts = pathname.split("/")
        parts[5] = DSSFile.get_epart_from_freq(df.index.freq)
        pathname = "/".join(parts)
        if isinstance(df.index, pd.PeriodIndex):
            if ctype.startswith("PER"):  # for period values...
                sp = df.index.shift(1).to_timestamp()[
                    0
                ]  # shift by 1 as per HEC convention
            else:
                raise 'Either pass in ctype beginning with "PER" ' + "for period indexed dataframe or change dataframe to timestamps"
        else:
            sp = df.index[0]
        # values are either the first column in the pandas DataFrame or should be a pandas Series
        values = (
            df.iloc[:, 0].values if isinstance(df, pd.DataFrame) else df.iloc[:].values
        )
        values = np.ascontiguousarray(values, dtype="d")
        istat = pyheclib.hec_zsrtsxd(
            self.ifltab,
            pathname,
            sp.strftime("%d%b%Y").upper(),
            sp.round(freq="min").strftime("%H%M"),
            values,
            cunits[:8],
            ctype[:8],
        )
        self._respond_to_istat_state(istat)

    def read_its(
        self, pathname, startDateStr=None, endDateStr=None, guess_vals_per_block=10000
    ):
        """
        reads the entire irregular time series record. The timewindow is derived
        from the D-PART of the pathname so make sure to read that from the catalog
        before calling this function
        """
        if pathname:
            pathname = pathname.upper()
        epart = self.parse_pathname_epart(pathname)
        startDateStr, endDateStr = self._parse_times(pathname, startDateStr, endDateStr)
        startDateStr = (
            pd.to_datetime(startDateStr).floor("1D").strftime("%d%b%Y").upper()
        )  # round down
        endDateStr = (
            pd.to_datetime(endDateStr).ceil("1D").strftime("%d%b%Y").upper()
        )  # round up
        juls, istat = pyheclib.hec_datjul(startDateStr)
        jule, istat = pyheclib.hec_datjul(endDateStr)
        ietime = istime = 0
        # guess how many values to be read based on e part approximation
        ktvals = DSSFile._number_between(
            startDateStr, endDateStr, DSSFile._get_timedelta_for_interval(epart)
        )
        ktvals = guess_vals_per_block * int(ktvals)
        kdvals = ktvals
        itimes = np.zeros(ktvals, "i")
        dvalues = np.zeros(kdvals, "d")
        inflag = 0  # Retrieve both values preceding and following time window in addtion to time window
        nvals, ibdate, cunits, ctype, istat = pyheclib.hec_zritsxd(
            self.ifltab, pathname, juls, istime, jule, ietime, itimes, dvalues, inflag
        )

        self._respond_to_istat_state(istat)
        if nvals == ktvals:
            raise Exception(
                "More values than guessed! %d. Call with guess_vals_per_block > 10000 "
                % ktvals
            )
        base_date = parse("31DEC1899") + timedelta(days=ibdate)
        df = pd.DataFrame(
            dvalues[:nvals],
            index=base_date + DSSFile.timedelta_minutes(itimes[:nvals]),
            columns=[pathname],
        )
        return DSSData(data=df, units=cunits.strip(), period_type=ctype.strip())
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
        if pathname:
            pathname = pathname.upper()
        parts = pathname.split("/")
        # parts[5]=DSSFile.FREQ_EPART_MAP[df.index.freq]
        if interval:
            parts[5] = interval
        else:
            if len(parts[5]) == 0:
                raise Exception(
                    "Specify interval = IR-YEAR or IR-MONTH or IR-DAY or provide it the pathname (5th position)"
                )
        epart = parts[5]
        if len(parts[4]) == 0:
            startDateStr = (
                (df.index[0] - pd.offsets.YearBegin(1)).strftime("%d%b%Y").upper()
            )
            endDateStr = (
                (df.index[-1] + pd.offsets.YearBegin(0)).strftime("%d%b%Y").upper()
            )
            parts[4] = startDateStr + " - " + endDateStr
        else:
            tw = list(map(lambda x: x.strip(), parts[4].split("-")))
            startDateStr = tw[0]
            endDateStr = tw[1]  # self._pad_to_end_of_block(tw[1],epart)
        juls, istat = pyheclib.hec_datjul(startDateStr)
        jule, istat = pyheclib.hec_datjul(endDateStr)
        ietime = istime = 0
        pathname = "/".join(parts)
        itimes = df.index - parse(startDateStr)
        itimes = itimes.total_seconds() / 60  # time in minutes since base date juls
        itimes = itimes.values.astype("i")  # conver to integer numpy
        inflag = 1  # replace data (merging should be done in memory)
        # values are either the first column in the pandas DataFrame or should be a pandas Series
        values = (
            df.iloc[:, 0].values if isinstance(df, pd.DataFrame) else df.iloc[:].values
        )
        istat = pyheclib.hec_zsitsxd(
            self.ifltab, pathname, itimes, values, juls, cunits, ctype, inflag
        )
        self._respond_to_istat_state(istat)
        # return istat
