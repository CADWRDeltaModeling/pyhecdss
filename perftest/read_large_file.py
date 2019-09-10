import pyhecdss
import datetime
if __name__=='__main__':
    pyhecdss.set_message_level(0)
    d=pyhecdss.DSSFile('./ITP_PP_out_ec.dss')
    s=datetime.datetime.now()
    catdf=d.read_catalog()
    print('catalog read in :', datetime.datetime.now()-s )
    plist=d.get_pathnames()
    print('Reading ',len(plist),'...')
    s=datetime.datetime.now()
    for path in plist:
        si=datetime.datetime.now()
        df,u,p=d.read_rts(path)
        print('read ',path,' in ',datetime.datetime.now()-si)
    print('read all in ',datetime.datetime.now()-s)
