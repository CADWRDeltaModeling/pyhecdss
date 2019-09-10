import vutils
import datetime
if __name__=='__main__':
    print('Uses Vista which wraps lowlevel HEC DSSVue functions')
    d=vutils.opendss('ITP_PP_out_ec.dss')
    s=datetime.datetime.now()
    npaths=len(d) # Used to load the catalog into memory
    print('Catalog read in %s'%str(datetime.datetime.now()-s))
    print('Reading data from %s pathnames'%str(npaths))
    s=datetime.datetime.now()
    for ref in d:
        s1=datetime.datetime.now()
        data=ref.getData()
        path=ref.getPathname()
        print('Read %s in %s '%(str(path), str(datetime.datetime.now()-s1)))
    print('Read %s in  %s'%(npaths,str(datetime.datetime.now()-s)))