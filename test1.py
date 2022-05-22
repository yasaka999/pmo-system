sqlmovie= 'select contentname,a.code moviecode,fileurl,b.code programcode,c.MediaSpec MediaSpec,type,SCREEN_FORMAT from \
    mediacontent a,program b ,contentdef c where a.ContentDefID=c.ContentDefID and a.status="4"  and mediacontentid in ( \
        select  mediacontentid from programmediacontent where objtype= "1" and objid=%d) and b.programid=%d' % ((rs[0]),rs[0])
  