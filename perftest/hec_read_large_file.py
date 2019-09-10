from hec.heclib.dss import HecDSSUtilities
from hec.heclib.dss import HecDss
import datetime
if __name__=='__main__':
    print('Run with vscript. Uses HEC-DSSVue functions to do the same as read_large_file.py')
    HecDSSUtilities.setMessageLevel(0)
    d=HecDss.open('ITP_PP_out_ec.dss',1)
    s=datetime.datetime.now()
    plist=d.getCondensedCatalog()
    print('Catalog read in %s'%str(datetime.datetime.now()-s))
    print('Reading data from %s pathnames'%len(plist))
    s=datetime.datetime.now()
    for path in plist:
        s1=datetime.datetime.now()
        data=d.get(str(path),1)
        print('Read %s in %s '%(str(path), str(datetime.datetime.now()-s1)))
    print('Read %s in  %s'%(len(plist),str(datetime.datetime.now()-s)))