from vtools.datastore.dss.api import *
import datetime

if __name__ == '__main__':
    fname="ITP_PP_out_ec.dss"
    s=datetime.datetime.now()
    c=dss_catalog(fname)
    print('catalog read in : %s'%str(datetime.datetime.now()-s) )
    print('Reading %d ...'%len(c))
    s=datetime.datetime.now()
    for e in c:
        #e[0].item_names() --> ['A', 'C', 'B', 'E', 'D', 'F', 'interval']
        path = '/'+e.item('A')+'/'+e.item('B')+'/'+e.item('C')+'//'+e.item('E')+'/'+e.item('F')+'/'
        si=datetime.datetime.now()
        dss_retrieve_ts(fname,path)
        print('read %s in %s'%(path, str(datetime.datetime.now()-si)))
    print('read all in %s'%str(datetime.datetime.now()-s))
