CREATE OR REPLACE procedure BTO_C2.pro_cre_programtag(icode    IN varchar2,
                                               iioptags IN varchar2,
                                               iiposter IN varchar2,
                                               iistill  IN varchar2,
                                               iiopimg1 IN varchar2,
                                               iiopimg2 IN varchar2,
                                               itag     IN varchar2,
                                               isysid   IN varchar2) is
  --声明变量
  icount1 number(10);
  icount2 number(10);
  icount3 number(10);
  ilabecount number(10);
  --ioptags     varchar2(4000);
  istatus2    varchar2(16);
  istatus3    varchar2(16);
  inewoptags  varchar2(4000);
  istatus     program.status%type;
  iseriesflag program.seriesflag%type;
  ideleteflag program.deleteflag%type;
  --icode       program.code%type;
  iname        program.name%type;
  idirectors   program.director%type;
  basemarkName VARCHAR2(130);
  opmarkName   VARCHAR2(130);
  itypeid      program.typeid%type;
  iCOLUMNNAME  type.NAME%type;
  icasts       program.kpeople%type;
  iwriters     program.scriptwriter%type;
  iyear        program.releaseyear%type;
  itags        program.Tags%type;
  ilabeltype   program.labeltype%type;
  ilabeltypetmp   program.labeltype%type;
  ilanguages   program.language%type;
  iduration    program.duration%type;
  igenres      program.genre%type;
  --
  icountries            program.countries%type;
  ivspid                program.vspid%type;
  iTITLE_SEARCH_NAME    program.TITLE_SEARCH_NAME%type;
  isummary              program.description%type;
  typeid                program.typeid%type;
  ibastags              program.bastags%type;
  ipgname               VARCHAR2(4000);
  ipgcode               VARCHAR2(4000);
  ichargetype           VARCHAR2(255);
  icompere              program.COMPERE%type;
  iprogramid            programtag.programid%type;
  iopmark               programtag.opmark%type;
  ibasemark             programtag.basemark%type;
  iscore                programtag.score%type;
  iideleteflag          programtag.deleteflag%type;
  ilicensingwindowstart programtag.licensingwindowstart%type;
  ilicensingwindowend   programtag.licensingwindowend%type;
  inewposter            varchar2(4000);
  inewstill             varchar2(4000);
  inewopimg1            varchar2(4000);
  inewopimg2            varchar2(4000);
  itempstatus           varchar2(10);
  icontentid            varchar2(255);
  itempcount            number;
begin
  /*
  同步programtag  code sysid  触发类型:u 更新 a 添加 d 删除 必传入参数
  增加记录后 传入code sysid tag
  在更新记录之前传入 code 和没有变更之前的字段值 optags poster still opimg1 opimg2
  在在删除记录之前传入 code
  */
  --ioldoptags := iioptags;
  iCOLUMNNAME := '';
  begin
    select p.name,
           replace(director, '|', ''),
           p.typeid,
           kpeople,
           compere,
           replace(p.scriptwriter, '|', ''),
           p.RELEASEYEAR,
           p.tags,
           p.labeltype,
           replace(p.language, '|', ''),
           replace(p.countries, '|', ''),
           p.vspid2,
           p.TITLE_SEARCH_NAME,
           p.duration,
           genre,
           p.description,
           seriesflag,
           p.status,
           p.bastags,
           p.deleteflag
      into iname,
           idirectors,
           itypeid,
           icasts,
           icompere,
           iwriters,
           iyear,
           itags,
           ilabeltype,
           ilanguages,
           icountries,
           ivspid,
           iTITLE_SEARCH_NAME,
           iduration,
           igenres,
           isummary,
           iseriesflag,
           istatus,
           ibastags,
           ideleteflag
      from program p
     where p.code = icode;
  exception
    when others then
      null;
  end;
  SELECT count(*)
    INTO icount3
    FROM programtag w
   WHERE w.code = icode
     and w.sysid = isysid;
  opmarkName   := '';
  basemarkName := '';
  IF icount3 > 0 THEN
    select optags,
           poster,
           still,
           opimg1,
           opimg2,
           licensingwindowstart,
           licensingwindowend,
           deleteflag,
           programid,
           opmark,
           basemark,
           contentid,
           a.pgname pgname,
           a.pgcode pgcode,
           a.chargetype chargetype,
           score
      into inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ilicensingwindowstart,
           ilicensingwindowend,
           iideleteflag,
           iprogramid,
           iopmark,
           ibasemark,
           icontentid,
           ipgname,
           ipgcode,
           ichargetype,
           iscore
      from programtag p
      left join (select p.code,
                    pg.sysid,
                    listagg(pg.name, '|') within group(order by pg.name) pgname,
                    listagg(pg.code, '|') within group(order by pg.code) pgcode,
                    listagg(pg.CHARGETYPE, '|') within group(order by pg.CHARGETYPE) CHARGETYPE
               from programtag p
               left join bto_c2.packagedtl pd
                 on pd.MEDIACODE = p.code
               left join bto_c2.package pg
                 on pg.PACKAGEID = pd.PACKAGEID
             where pg.deleteflag='0'
              group by p.code, pg.sysid) a
    on p.code = a.code and p.sysid = a.sysid
     where p.code = icode
       and p.sysid = isysid;
    --更新ws_mergedmedia 的角标字段
    begin
      if (iopmark is not null) then
        select k.icon
          into opmarkName
          from commark k
         where k.code = iopmark
           and k.sysid = isysid;
      end if;
    exception
      when others then
        dbms_output.put_line('oracle tyid is null code:' || itypeid ||
                             'error message:' || substr(SQLERRM, 1, 100));
        null;
    end;
    begin
      ilabeltypetmp :='';
      if (ilabeltype is not null) then
         select count(*) into ilabecount
         FROM DUAL
        where instr(ilabeltype,'1080i')>0
        or instr(ilabeltype,'1080p')>0
        or instr(ilabeltype,'1080P')>0;
        if ilabecount = 1 then
           ilabeltypetmp :='1';
        end if;
        select count(*) into ilabecount
         FROM DUAL
        where instr(ilabeltype,'1740P')>0
        or instr(ilabeltype,'2160P')>0
        or instr(ilabeltype,'4096')>0
        or instr(ilabeltype,'3840')>0;
        if ilabecount = 1 then
          ilabeltypetmp :='2';
          end if;
        select count(*) into ilabecount
         FROM DUAL
        where instr(ilabeltype,'296P')>0
        or instr(ilabeltype,'360P')>0
        or instr(ilabeltype,'400P')>0
        or instr(ilabeltype,'528P')>0
        or instr(ilabeltype,'540P')>0
        or instr(ilabeltype,'576i')>0
        or instr(ilabeltype,'576P')>0
        or instr(ilabeltype,'720P')>0
        or instr(ilabeltype,'404P')>0;
        if ilabecount = 1 then
          ilabeltypetmp :='0';
          end if;
      end if;
    exception
      when others then
        dbms_output.put_line('oracle ilabeltype is null code:' || ilabeltype ||
                             'error message:' || substr(SQLERRM, 1, 100));
        null;
    end;
    ilabeltype :=ilabeltypetmp;
    begin
      if (ibasemark is not null) then
        select k.icon
          into basemarkName
          from commark k
         where k.code = ibasemark
           and k.sysid = isysid;
      end if;
    exception
      when others then
        dbms_output.put_line('oracle tyid is null code:' || itypeid ||
                             'error message:' || substr(SQLERRM, 1, 100));
        null;
    end;
    begin
      if (itypeid is not null) then
        select name
          into iCOLUMNNAME
          from bto_c2.type t
         where t.code = itypeid;
      end if;
    exception
      when others then
        dbms_output.put_line('oracle tyid is null code:' || itypeid ||
                             'error message:' || substr(SQLERRM, 1, 100));
        null;
    end;
  end if;
  if iseriesflag = '0' then
    if itag = 'a' then
      select count(*)
        into icount1
        from credb.ws_mergedmedia
       where c2code = icode;
      select count(*)
        into icount2
        from credb.ws_process
       where code = icode;
      if icount2 = 0 then
        --新增记录到credb.WS_PROCESS
        insert into credb.WS_PROCESS
          (PROCESSID,
           type,
           CODE,
           name,
           PROCESSTIME,
           PROCESSRESULT,
           PROCESSMEMO,
           LASTFILETIME,
           FILTERTIME,
           FILTERRESULT,
           FILTERMEMO,
           AUDITRESULT,
           AUDITTIME,
           AUDITMEMO,
           GENC2TIME,
           GENC2RESULT,
           GENC2MEMO,
           GENDOUBANRESULT,
           GENDOUBANMEMO)
        values
          (credb.seq_process.Nextval,
           'p',
           icode,
           iname,
           sysdate,
           1,
           null,
           null,
           null,
           1,
           null,
           1,
           null,
           null,
           null,
           null,
           null,
           null,
           null);
      end if;
      if icount1 > 0 then
        select status
          into istatus3
          from credb.ws_mergedmedia
         where c2code = icode;
        --deleteflag=1时，该平台状态为9
        if iideleteflag = 1 then
          if isysid = 't' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   toptags     = inewoptags,
                   tposter     = inewposter,
                   tstill      = inewstill,
                   topimg1     = inewopimg1,
                   topimg2     = inewopimg2,
                   tchargetype = ichargetype,
                   tchargecode = ipgcode,
                   tchargename = ipgname,
                   --更新角标字段
                   --topmark    = opmarkName,
                   topmark    = iopmark,
                   tbasemark  = basemarkName,
                   tscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagt  = '2',
                   status     = '9' || substr(istatus3, 2, 5),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_T = ilicensingwindowstart,
                   licensingwindowend_T   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'm' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   moptags     = inewoptags,
                   mposter     = inewposter,
                   mstill      = inewstill,
                   mopimg1     = inewopimg1,
                   mopimg2     = inewopimg2,
                   mchargetype = ichargetype,
                   mchargecode = ipgcode,
                   mchargename = ipgname,
                   --更新角标字段
                  -- mopmark    = opmarkName,
									 mopmark    = iopmark,
                   mbasemark  = basemarkName,
                   mscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagm  = '2',
                   status     = substr(istatus3, 1, 1) || '9' ||
                                substr(istatus3, 3, 4),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_M = ilicensingwindowstart,
                   licensingwindowend_M   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'u' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   uoptags     = inewoptags,
                   uposter     = inewposter,
                   ustill      = inewstill,
                   uopimg1     = inewopimg1,
                   uopimg2     = inewopimg2,
                   uchargetype = ichargetype,
                   uchargecode = ipgcode,
                   uchargename = ipgname,
                   --更新角标字段
                   --uopmark    = opmarkName,
									 uopmark    = iopmark,
                   ubasemark  = basemarkName,
                   uscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagu  = '2',
                   status     = substr(istatus3, 1, 2) || '9' ||
                                substr(istatus3, 4, 3),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_U = ilicensingwindowstart,
                   licensingwindowend_U   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   bastags                = ibastags,
                   labeltype              = ilabeltype,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'a' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   aoptags     = inewoptags,
                   aposter     = inewposter,
                   astill      = inewstill,
                   aopimg1     = inewopimg1,
                   aopimg2     = inewopimg2,
                   achargetype = ichargetype,
                   achargecode = ipgcode,
                   achargename = ipgname,
                   --更新角标字段
                   aopmark    = opmarkName,
                   abasemark  = basemarkName,
                   ascore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflaga  = '2',
                   status     = substr(istatus3, 1, 3) || '9' ||
                                substr(istatus3, 5, 2),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_A = ilicensingwindowstart,
                   licensingwindowend_A   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'b' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   boptags     = inewoptags,
                   bposter     = inewposter,
                   bstill      = inewstill,
                   bopimg1     = inewopimg1,
                   bopimg2     = inewopimg2,
                   bchargetype = ichargetype,
                   bchargecode = ipgcode,
                   bchargename = ipgname,
                   --更新角标字段
                   bopmark    = opmarkName,
                   bbasemark  = basemarkName,
                   bscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagb  = '2',
                   status     = substr(istatus3, 1, 4) || '9' ||
                                substr(istatus3, 6, 1),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_B = ilicensingwindowstart,
                   licensingwindowend_B   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'c' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   coptags     = inewoptags,
                   cposter     = inewposter,
                   cstill      = inewstill,
                   copimg1     = inewopimg1,
                   copimg2     = inewopimg2,
                   cchargetype = ichargetype,
                   cchargecode = ipgcode,
                   cchargename = ipgname,
                   --更新角标字段
                   copmark    = opmarkName,
                   cbasemark  = basemarkName,
                   cscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagc  = '2',
                   status     = substr(istatus3, 1, 5) || '9',
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_C = ilicensingwindowstart,
                   licensingwindowend_C   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          end if;
        else
          if isysid = 't' then
            select count(*)
              into itempcount
              from view_categorydtl_t
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := '0' || substr(istatus3, 2, 5);
            else
              itempstatus := '9' || substr(istatus3, 2, 5);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   toptags     = inewoptags,
                   tposter     = inewposter,
                   tstill      = inewstill,
                   topimg1     = inewopimg1,
                   topimg2     = inewopimg2,
                   tchargetype = ichargetype,
                   tchargecode = ipgcode,
                   tchargename = ipgname,
                   --更新角标字段
                   topmark    = iopmark,
                   tbasemark  = ibasemark,
                   tscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagt  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_T = ilicensingwindowstart,
                   licensingwindowend_T   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'm' then
            select count(*)
              into itempcount
              from view_categorydtl_m
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 1) || '0' ||
                             substr(istatus3, 3, 4);
            else
              itempstatus := substr(istatus3, 1, 1) || '9' ||
                             substr(istatus3, 3, 4);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   moptags     = inewoptags,
                   mposter     = inewposter,
                   mstill      = inewstill,
                   mopimg1     = inewopimg1,
                   mopimg2     = inewopimg2,
                   mchargetype = ichargetype,
                   mchargecode = ipgcode,
                   mchargename = ipgname,
                   --更新角标字段
                   --mopmark    = opmarkName,
									 mopmark    = iopmark,
                   mbasemark  = basemarkName,
                   mscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagm  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_M = ilicensingwindowstart,
                   licensingwindowend_M   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'u' then
            select count(*)
              into itempcount
              from view_categorydtl_u
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 2) || '0' ||
                             substr(istatus3, 4, 3);
            else
              itempstatus := substr(istatus3, 1, 2) || '9' ||
                             substr(istatus3, 4, 3);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   uoptags     = inewoptags,
                   uposter     = inewposter,
                   ustill      = inewstill,
                   uopimg1     = inewopimg1,
                   uopimg2     = inewopimg2,
                   uchargetype = ichargetype,
                   uchargecode = ipgcode,
                   uchargename = ipgname,
                   --更新角标字段
                  -- uopmark    = opmarkName,
									 uopmark    = iopmark,
                   ubasemark  = basemarkName,
                   uscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagu  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_U = ilicensingwindowstart,
                   licensingwindowend_U   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'a' then
            select count(*)
              into itempcount
              from view_categorydtl_a
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 3) || '0' ||
                             substr(istatus3, 5, 2);
            else
              itempstatus := substr(istatus3, 1, 3) || '9' ||
                             substr(istatus3, 5, 2);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   aoptags     = inewoptags,
                   aposter     = inewposter,
                   astill      = inewstill,
                   aopimg1     = inewopimg1,
                   aopimg2     = inewopimg2,
                   achargetype = ichargetype,
                   achargecode = ipgcode,
                   achargename = ipgname,
                   --更新角标字段
                   aopmark    = opmarkName,
                   abasemark  = basemarkName,
                   ascore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflaga  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_A = ilicensingwindowstart,
                   licensingwindowend_A   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'b' then
            select count(*)
              into itempcount
              from view_categorydtl_b
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 4) || '0' ||
                             substr(istatus3, 6, 1);
            else
              itempstatus := substr(istatus3, 1, 4) || '9' ||
                             substr(istatus3, 6, 1);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   boptags     = inewoptags,
                   bposter     = inewposter,
                   bstill      = inewstill,
                   bopimg1     = inewopimg1,
                   bopimg2     = inewopimg2,
                   bchargetype = ichargetype,
                   bchargecode = ipgcode,
                   bchargename = ipgname,
                   --更新角标字段
                   bopmark    = opmarkName,
                   bbasemark  = basemarkName,
                   bscore     = iscore,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   syncflagb  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_B = ilicensingwindowstart,
                   licensingwindowend_B   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'c' then
            select count(*)
              into itempcount
              from view_categorydtl_c
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 5) || '0';
            else
              itempstatus := substr(istatus3, 1, 5) || '9';
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   coptags     = inewoptags,
                   cposter     = inewposter,
                   cstill      = inewstill,
                   copimg1     = inewopimg1,
                   copimg2     = inewopimg2,
                   cchargetype = ichargetype,
                   cchargecode = ipgcode,
                   cchargename = ipgname,
                   --更新角标字段
                   copmark    = opmarkName,
                   cbasemark  = basemarkName,
                   cscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagc  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_C = ilicensingwindowstart,
                   licensingwindowend_C   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                    contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          end if;
        end if;
        insert into sp_operation_log
          (code, action, table_name, msg)
        values
          (iCODE, 'insert', 'programtag', 'succeed');
      elsif icount1 = 0 then
        if iideleteflag = 0 then
          if isysid = 't' then
            select count(*)
              into itempcount
              from view_categorydtl_t
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '099999';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'm' then
            select count(*)
              into itempcount
              from view_categorydtl_m
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '909999';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'u' then
            select count(*)
              into itempcount
              from view_categorydtl_m
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '990999';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'a' then
            select count(*)
              into itempcount
              from view_categorydtl_a
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '999099';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'b' then
            select count(*)
              into itempcount
              from view_categorydtl_b
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '999909';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'c' then
            select count(*)
              into itempcount
              from view_categorydtl_c
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '999990';
            else
              istatus2 := '999999';
            end if;
          end if;
        else
          istatus2 := '999999';
        end if;
        if (itypeid is not null) then
          select name
            into iCOLUMNNAME
            from bto_c2.type t
           where t.code = itypeid;
        end if;
        insert into credb.ws_mergedmedia
          (directors,
           columntype,
           COLUMNNAME,
           casts,
           compere,
           sourcecasts,
           sourcedirectors,
           writers,
           year,
           tags,
           labeltype,
           languages,
           countries,
           vspid,
           searchname,
           durations,
           genres,
           summary,
           type,
           c2code,
           name,
           datamode,
           updatetime,
           seqid,
           status,
           bastags,
           toptags,
           tposter,
           tstill,
           topimg1,
           topimg2,
           tchargetype,
           tchargecode,
           tchargename,
           --更新角标字段
           topmark,
           tbasemark,
           tscore,
           moptags,
           mposter,
           mstill,
           mopimg1,
           mopimg2,
           mchargetype,
           mchargecode,
           mchargename,
           --更新角标字段
           mopmark,
           mbasemark,
           mscore,
           uoptags,
           uposter,
           ustill,
           uopimg1,
           uopimg2,
           uchargetype,
           uchargecode,
           uchargename,
           --更新角标字段
           uopmark,
           ubasemark,
           uscore,
           aoptags,
           aposter,
           astill,
           aopimg1,
           aopimg2,
           achargetype,
           achargecode,
           achargename,
           --更新角标字段
           aopmark,
           abasemark,
           ascore,
           boptags,
           bposter,
           bstill,
           bopimg1,
           bopimg2,
           bchargetype,
           bchargecode,
           bchargename,
           --更新角标字段
           bopmark,
           bbasemark,
           bscore,
           coptags,
           cposter,
           cstill,
           copimg1,
           copimg2,
           cchargetype,
           cchargecode,
           cchargename,
           --更新角标字段
           copmark,
           cbasemark,
           cscore,
           licensingwindowstart_T,
           licensingwindowend_T,
           licensingwindowstart_M,
           licensingwindowend_M,
           licensingwindowstart_U,
           licensingwindowend_U,
           licensingwindowstart_A,
           licensingwindowend_A,
           licensingwindowstart_B,
           licensingwindowend_B,
           licensingwindowstart_C,
           licensingwindowend_C,
           json_status,
            contentid,
           syncflagt,
           syncflagm,
           syncflagu,
           syncflaga,
           syncflagb,
           syncflagc)
        values
          (idirectors,
           itypeid,
           iCOLUMNNAME,
           icasts,
           icompere,
           icasts,
           idirectors,
           iwriters,
           iyear,
           itags,
           ilabeltype,
           ilanguages,
           icountries,
           ivspid,
           iTITLE_SEARCH_NAME,
           iduration,
           igenres,
           isummary,
           'p',
           icode,
           iname,
           'c',
           to_char(sysdate, 'yyyy-mm-dd hh24:mi:ss'),
           credb.SEQ_MERGEDMEDIA_SEQID.Nextval,
           istatus2,
           ibastags,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,

           --更新角标字段
           iopmark,
           ibasemark,
           iscore,
           inewoptags,
           inewposter
           decode(isysid,'t',inewposter,null)
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           iopmark,
           ibasemark,
           iscore,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           iopmark,
           ibasemark,
           iscore,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           iopmark,
           ibasemark,
           iscore,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           iopmark,
           ibasemark,
           iscore,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           iopmark,
           ibasemark,
           iscore,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           '0',
           icontentid,
           '2',
           '2',
           '2',
           '2',
           '2',
           '2');
        insert into sp_operation_log
          (code, action, table_name, msg)
        values
          (icode, 'insert', 'programtag', 'succeed');
      end if;
    elsif itag = 'u' then
      select count(*)
        into icount1
        from credb.ws_mergedmedia
       where c2code = icode;
if icount1 > 0 then
      select status
        into istatus3
        from credb.ws_mergedmedia
       where c2code = icode;

        if iideleteflag = 1 then
          if isysid = 't' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   toptags     = inewoptags,
                   tposter     = inewposter,
                   tstill      = inewstill,
                   topimg1     = inewopimg1,
                   topimg2     = inewopimg2,
                   tchargetype = ichargetype,
                   tchargecode = ipgcode,
                   tchargename = ipgname,
                   --更新角标字段
                   --topmark    = opmarkName,
                    topmark    = iopmark,
                   tbasemark  = basemarkName,
                   tscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagt  = '2',
                   status     = '9' || substr(istatus3, 2, 5),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_T = ilicensingwindowstart,
                   licensingwindowend_T   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'm' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   moptags     = inewoptags,
                   mposter     = inewposter,
                   mstill      = inewstill,
                   mopimg1     = inewopimg1,
                   mopimg2     = inewopimg2,
                   mchargetype = ichargetype,
                   mchargecode = ipgcode,
                   mchargename = ipgname,
                   --更新角标字段
                  -- mopmark    = opmarkName,
								  mopmark    = iopmark,
                   mbasemark  = basemarkName,
                   mscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagm  = '2',
                   status     = substr(istatus3, 1, 1) || '9' ||
                                substr(istatus3, 3, 4),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_M = ilicensingwindowstart,
                   licensingwindowend_M   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'u' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   uoptags     = inewoptags,
                   uposter     = inewposter,
                   ustill      = inewstill,
                   uopimg1     = inewopimg1,
                   uopimg2     = inewopimg2,
                   uchargetype = ichargetype,
                   uchargecode = ipgcode,
                   uchargename = ipgname,
                   --更新角标字段
                   --uopmark    = opmarkName,
									 uopmark    = iopmark,
                   ubasemark  = basemarkName,
                   uscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagu  = '2',
                   status     = substr(istatus3, 1, 2) || '9' ||
                                substr(istatus3, 4, 3),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_U = ilicensingwindowstart,
                   licensingwindowend_U   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'a' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   aoptags     = inewoptags,
                   aposter     = inewposter,
                   astill      = inewstill,
                   aopimg1     = inewopimg1,
                   aopimg2     = inewopimg2,
                   achargetype = ichargetype,
                   achargecode = ipgcode,
                   achargename = ipgname,
                   --更新角标字段
                   aopmark    = opmarkName,
                   abasemark  = basemarkName,
                   ascore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflaga  = '2',
                   status     = substr(istatus3, 1, 3) || '9' ||
                                substr(istatus3, 5, 2),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_A = ilicensingwindowstart,
                   licensingwindowend_A   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'b' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   boptags     = inewoptags,
                   bposter     = inewposter,
                   bstill      = inewstill,
                   bopimg1     = inewopimg1,
                   bopimg2     = inewopimg2,
                   bchargetype = ichargetype,
                   bchargecode = ipgcode,
                   bchargename = ipgname,
                   --更新角标字段
                   bopmark    = opmarkName,
                   bbasemark  = basemarkName,
                   bscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagb  = '2',
                   status     = substr(istatus3, 1, 4) || '9' ||
                                substr(istatus3, 6, 1),
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_B = ilicensingwindowstart,
                   licensingwindowend_B   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'c' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   coptags     = inewoptags,
                   cposter     = inewposter,
                   cstill      = inewstill,
                   copimg1     = inewopimg1,
                   copimg2     = inewopimg2,
                   cchargetype = ichargetype,
                   cchargecode = ipgcode,
                   cchargename = ipgname,
                   --更新角标字段
                   copmark    = opmarkName,
                   cbasemark  = basemarkName,
                   cscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagc  = '2',
                   status     = substr(istatus3, 1, 5) || '9',
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_C = ilicensingwindowstart,
                   licensingwindowend_C   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          end if;
        else
          if isysid = 't' then
            select count(*)
              into itempcount
              from view_categorydtl_t
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := '0' || substr(istatus3, 2, 5);
            else
              itempstatus := '9' || substr(istatus3, 2, 5);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   toptags     = inewoptags,
                   tposter     = inewposter,
                   tstill      = inewstill,
                   topimg1     = inewopimg1,
                   topimg2     = inewopimg2,
                   tchargetype = ichargetype,
                   tchargecode = ipgcode,
                   tchargename = ipgname,
                   --更新角标字段
                   topmark    = iopmark,
                   tbasemark  = ibasemark,
                   tscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagt  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_T = ilicensingwindowstart,
                   licensingwindowend_T   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'm' then
            select count(*)
              into itempcount
              from view_categorydtl_m
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 1) || '0' ||
                             substr(istatus3, 3, 4);
            else
              itempstatus := substr(istatus3, 1, 1) || '9' ||
                             substr(istatus3, 3, 4);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   moptags     = inewoptags,
                   mposter     = inewposter,
                   mstill      = inewstill,
                   mopimg1     = inewopimg1,
                   mopimg2     = inewopimg2,
                   mchargetype = ichargetype,
                   mchargecode = ipgcode,
                   mchargename = ipgname,
                   --更新角标字段
                  -- mopmark    = opmarkName,
									mopmark    = iopmark,
                   mbasemark  = basemarkName,
                   mscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagm  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_M = ilicensingwindowstart,
                   licensingwindowend_M   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'u' then
            select count(*)
              into itempcount
              from view_categorydtl_u
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 2) || '0' ||
                             substr(istatus3, 4, 3);
            else
              itempstatus := substr(istatus3, 1, 2) || '9' ||
                             substr(istatus3, 4, 3);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   uoptags     = inewoptags,
                   uposter     = inewposter,
                   ustill      = inewstill,
                   uopimg1     = inewopimg1,
                   uopimg2     = inewopimg2,
                   uchargetype = ichargetype,
                   uchargecode = ipgcode,
                   uchargename = ipgname,
                   --更新角标字段
                   uopmark    = iopmark,
                   ubasemark  = basemarkName,
                   uscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagu  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_U = ilicensingwindowstart,
                   licensingwindowend_U   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'a' then
            select count(*)
              into itempcount
              from view_categorydtl_a
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 3) || '0' ||
                             substr(istatus3, 5, 2);
            else
              itempstatus := substr(istatus3, 1, 3) || '9' ||
                             substr(istatus3, 5, 2);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   aoptags     = inewoptags,
                   aposter     = inewposter,
                   astill      = inewstill,
                   aopimg1     = inewopimg1,
                   aopimg2     = inewopimg2,
                   achargetype = ichargetype,
                   achargecode = ipgcode,
                   achargename = ipgname,
                   --更新角标字段
                   aopmark    = opmarkName,
                   abasemark  = basemarkName,
                   ascore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflaga  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_A = ilicensingwindowstart,
                   licensingwindowend_A   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'b' then
            select count(*)
              into itempcount
              from view_categorydtl_b
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 4) || '0' ||
                             substr(istatus3, 6, 1);
            else
              itempstatus := substr(istatus3, 1, 4) || '9' ||
                             substr(istatus3, 6, 1);
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   boptags     = inewoptags,
                   bposter     = inewposter,
                   bstill      = inewstill,
                   bopimg1     = inewopimg1,
                   bopimg2     = inewopimg2,
                   bchargetype = ichargetype,
                   bchargecode = ipgcode,
                   bchargename = ipgname,
                   --更新角标字段
                   bopmark    = opmarkName,
                   bbasemark  = basemarkName,
                   bscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagb  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_B = ilicensingwindowstart,
                   licensingwindowend_B   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'c' then
            select count(*)
              into itempcount
              from view_categorydtl_c
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              itempstatus := substr(istatus3, 1, 5) || '0';
            else
              itempstatus := substr(istatus3, 1, 5) || '9';
            end if;
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   coptags     = inewoptags,
                   cposter     = inewposter,
                   cstill      = inewstill,
                   copimg1     = inewopimg1,
                   copimg2     = inewopimg2,
                   cchargetype = ichargetype,
                   cchargecode = ipgcode,
                   cchargename = ipgname,
                   --更新角标字段
                   copmark    = opmarkName,
                   cbasemark  = basemarkName,
                   cscore     = iscore,
                   columntype = itypeid,
                   columnname = iCOLUMNNAME,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagc  = '2',
                   status     = itempstatus,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_C = ilicensingwindowstart,
                   licensingwindowend_C   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          end if;
        end if;
        if nvl(inewoptags, ' ') != nvl(iioptags, ' ') or
           nvl(inewposter, ' ') != nvl(iiposter, ' ') or
           nvl(inewstill, ' ') != nvl(iistill, ' ') or
           nvl(inewopimg1, ' ') != nvl(iiopimg1, ' ') or
           nvl(inewopimg2, ' ') != nvl(iiopimg2, ' ') then
          if isysid = 't' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   toptags     = inewoptags,
                   tposter     = inewposter,
                   tstill      = inewstill,
                   topimg1     = inewopimg1,
                   topimg2     = inewopimg2,
                   tchargetype = ichargetype,
                   tchargecode = ipgcode,
                   tchargename = ipgname,
                   --更新角标字段
                   --topmark    = opmarkName,
                    topmark    = iopmark,
                   tbasemark  = basemarkName,
                   tscore     = iscore,
                   columntype = itypeid,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagt  = '2',
                   columnname = iCOLUMNNAME,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_T = ilicensingwindowstart,
                   licensingwindowend_T   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'm' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   moptags     = inewoptags,
                   mposter     = inewposter,
                   mstill      = inewstill,
                   mopimg1     = inewopimg1,
                   mopimg2     = inewopimg2,
                   mchargetype = ichargetype,
                   mchargecode = ipgcode,
                   mchargename = ipgname,
                   --更新角标字段
                  -- mopmark    = opmarkName,
									 mopmark    =  iopmark,
                   mbasemark  = basemarkName,
                   mscore     = iscore,
                   columntype = itypeid,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagm  = '2',
                   columnname = iCOLUMNNAME,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_M = ilicensingwindowstart,
                   licensingwindowend_M   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'u' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   uoptags     = inewoptags,
                   uposter     = inewposter,
                   ustill      = inewstill,
                   uopimg1     = inewopimg1,
                   uopimg2     = inewopimg2,
                   uchargetype = ichargetype,
                   uchargecode = ipgcode,
                   uchargename = ipgname,
                   --更新角标字段
                  -- uopmark    = opmarkName,
									uopmark    = iopmark,
                   ubasemark  = basemarkName,
                   uscore     = iscore,
                   columntype = itypeid,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagu  = '2',
                   columnname = iCOLUMNNAME,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_U = ilicensingwindowstart,
                   licensingwindowend_U   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'a' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   aoptags     = inewoptags,
                   aposter     = inewposter,
                   astill      = inewstill,
                   aopimg1     = inewopimg1,
                   aopimg2     = inewopimg2,
                   achargetype = ichargetype,
                   achargecode = ipgcode,
                   achargename = ipgname,
                   --更新角标字段
                   aopmark    = opmarkName,
                   abasemark  = basemarkName,
                   ascore     = iscore,
                   columntype = itypeid,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflaga  = '2',
                   columnname = iCOLUMNNAME,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_A = ilicensingwindowstart,
                   licensingwindowend_A   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'b' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   boptags     = inewoptags,
                   bposter     = inewposter,
                   bstill      = inewstill,
                   bopimg1     = inewopimg1,
                   bopimg2     = inewopimg2,
                   bchargetype = ichargetype,
                   bchargecode = ipgcode,
                   bchargename = ipgname,
                   --更新角标字段
                   bopmark    = opmarkName,
                   bbasemark  = basemarkName,
                   bscore     = iscore,
                   columntype = itypeid,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagb  = '2',
                   columnname = iCOLUMNNAME,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_B = ilicensingwindowstart,
                   licensingwindowend_B   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          elsif isysid = 'c' then
            update credb.ws_mergedmedia
               set json_status = '0',
                   name        = iname,
                   coptags     = inewoptags,
                   cposter     = inewposter,
                   cstill      = inewstill,
                   copimg1     = inewopimg1,
                   copimg2     = inewopimg2,
                   cchargetype = ichargetype,
                   cchargecode = ipgcode,
                   cchargename = ipgname,
                   --更新角标字段
                   copmark    = opmarkName,
                   cbasemark  = basemarkName,
                   cscore     = iscore,
                   columntype = itypeid,
                   updatetime = to_char(sysdate, 'yyyymmddhh24miss'),
                   updater    = 'prot',
                   syncflagc  = '2',
                   columnname = iCOLUMNNAME,
                   --
                   languages              = ilanguages,
                   countries              = icountries,
                   vspid                  = ivspid,
                   genres                 = igenres,
                   searchname             = iTITLE_SEARCH_NAME,
                   licensingwindowstart_C = ilicensingwindowstart,
                   licensingwindowend_C   = ilicensingwindowend,
                   DIRECTORS              = idirectors,
                   CASTS                  = icasts,
                   compere                = icompere,
                   SOURCECASTS            = icasts,
                   year                   = iyear,
                   tags                   = itags,
                   labeltype              = ilabeltype,
                   bastags                = ibastags,
                   contentid              = icontentid,
                   SOURCEDIRECTORS        = idirectors
             where c2code = icode;
          end if;
        else
          null;
        end if;
        insert into sp_operation_log
          (code, action, table_name, msg)
        values
          (iCODE, 'update', 'programtag', 'succeed');
      elsif icount1 = 0 then
        if iideleteflag = 0 then
          if isysid = 't' then
            select count(*)
              into itempcount
              from view_categorydtl_t
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '099999';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'm' then
            select count(*)
              into itempcount
              from view_categorydtl_m
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '909999';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'u' then
            select count(*)
              into itempcount
              from view_categorydtl_u
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '990999';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'a' then
            select count(*)
              into itempcount
              from view_categorydtl_a
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '999099';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'b' then
            select count(*)
              into itempcount
              from view_categorydtl_b
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '999909';
            else
              istatus2 := '999999';
            end if;
          elsif isysid = 'c' then
            select count(*)
              into itempcount
              from view_categorydtl_c
             where objid = iprogramid
               and objtype = '8';
            if itempcount > 0 then
              istatus2 := '999990';
            else
              istatus2 := '999999';
            end if;
          end if;
        else
          istatus2 := '999999';
        end if;
        if (itypeid is not null) then
          select name
            into iCOLUMNNAME
            from bto_c2.type t
           where t.code = itypeid;
        end if;
        insert into credb.ws_mergedmedia
          (directors,
           columntype,
           COLUMNNAME,
           casts,
           compere,
           sourcecasts,
           sourcedirectors,
           writers,
           year,
           tags,
           labeltype,
           languages,
           countries,
           vspid,
           searchname,
           durations,
           genres,
           summary,
           type,
           c2code,
           name,
           datamode,
           updatetime,
           seqid,
           status,
           bastags,
           toptags,
           tposter,
           tstill,
           topimg1,
           topimg2,
           tchargetype,
           tchargecode,
           tchargename,
           --更新角标字段
           topmark,
           tbasemark,
           tscore,
           moptags,
           mposter,
           mstill,
           mopimg1,
           mopimg2,
           mchargetype,
           mchargecode,
           mchargename,
           --更新角标字段
           mopmark,
           mbasemark,
           mscore,
           uoptags,
           uposter,
           ustill,
           uopimg1,
           uopimg2,
           uchargetype,
           uchargecode,
           uchargename,
           --更新角标字段
           uopmark,
           ubasemark,
           uscore,
           aoptags,
           aposter,
           astill,
           aopimg1,
           aopimg2,
           achargetype,
           achargecode,
           achargename,
           --更新角标字段
           aopmark,
           abasemark,
           ascore,
           boptags,
           bposter,
           bstill,
           bopimg1,
           bopimg2,
           bchargetype,
           bchargecode,
           bchargename,
           --更新角标字段
           bopmark,
           bbasemark,
           bscore,
           coptags,
           cposter,
           cstill,
           copimg1,
           copimg2,
           cchargetype,
           cchargecode,
           cchargename,
           --更新角标字段
           copmark,
           cbasemark,
           cscore,
           licensingwindowstart_T,
           licensingwindowend_T,
           licensingwindowstart_M,
           licensingwindowend_M,
           licensingwindowstart_U,
           licensingwindowend_U,
           licensingwindowstart_A,
           licensingwindowend_A,
           licensingwindowstart_B,
           licensingwindowend_B,
           licensingwindowstart_C,
           licensingwindowend_C,
           json_status,
           contentid,
           syncflagt,
           syncflagm,
           syncflagu,
           syncflaga,
           syncflagb,
           syncflagc)
        values
          (idirectors,
           itypeid,
           iCOLUMNNAME,
           icasts,
           icompere,
           icasts,
           idirectors,
           iwriters,
           iyear,
           itags,
           ilabeltype,
           ilanguages,
           icountries,
           ivspid,
           iTITLE_SEARCH_NAME,
           iduration,
           igenres,
           isummary,
           'p',
           icode,
           iname,
           'c',
           to_char(sysdate, 'yyyy-mm-dd hh24:mi:ss'),
           credb.SEQ_MERGEDMEDIA_SEQID.Nextval,
           istatus2,
           ibastags,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           opmarkName,
           basemarkName,
           iscore,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           opmarkName,
           basemarkName,
           iscore,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           opmarkName,
           basemarkName,
           iscore,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           opmarkName,
           basemarkName,
           iscore,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           opmarkName,
           basemarkName,
           iscore,
           inewoptags,
           inewposter,
           inewstill,
           inewopimg1,
           inewopimg2,
           ichargetype,
           ipgcode,
           ipgname,
           --更新角标字段
           opmarkName,
           basemarkName,
           iscore,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           ilicensingwindowstart,
           ilicensingwindowend,
           '0',
           icontentid,
           '2',
           '2',
           '2',
           '2',
           '2',
           '2');
        insert into sp_operation_log
          (code, action, table_name, msg)
        values
          (icode, 'update', 'programtag', 'succeed');
      end if;
    elsif itag = 'd' then
      select count(*)
        into icount1
        from credb.ws_mergedmedia
       where c2code = icode;
      select status
        into istatus3
        from credb.ws_mergedmedia
       where c2code = icode;
      if icount1 > 0 then
        if isysid = 't' then
          update credb.ws_mergedmedia
             set json_status = '0',
                 updatetime  = to_char(sysdate, 'yyyymmddhh24miss'),
                 updater     = 'prot',
                 syncflagt   = '2',
                 toptags     = '',
                 status      = '9' || substr(istatus3, 2, 5),
                 --
                 languages              = ilanguages,
                 countries              = icountries,
                 vspid                  = ivspid,
                 genres                 = igenres,
                 searchname             = iTITLE_SEARCH_NAME,
                 licensingwindowstart_T = ilicensingwindowstart,
                 licensingwindowend_T   = ilicensingwindowend,
                 DIRECTORS              = idirectors,
                 CASTS                  = icasts,
                 compere                = icompere,
                 SOURCECASTS            = icasts,
                 year                   = iyear,
                 tags                   = itags,
                 labeltype              = ilabeltype,
                 bastags                = ibastags,
                 contentid              = icontentid,
                 SOURCEDIRECTORS        = idirectors
           where c2code = icode;
        elsif isysid = 'm' then
          update credb.ws_mergedmedia
             set json_status = '0',
                 updatetime  = to_char(sysdate, 'yyyymmddhh24miss'),
                 updater     = 'prot',
                 syncflagm   = '2',
                 moptags     = '',
                 status      = substr(istatus3, 1, 1) || '9' ||
                               substr(istatus3, 3, 4),
                 --
                 languages              = ilanguages,
                 countries              = icountries,
                 vspid                  = ivspid,
                 genres                 = igenres,
                 searchname             = iTITLE_SEARCH_NAME,
                 licensingwindowstart_M = ilicensingwindowstart,
                 licensingwindowend_M   = ilicensingwindowend,
                 DIRECTORS              = idirectors,
                 CASTS                  = icasts,
                 SOURCECASTS            = icasts,
                 year                   = iyear,
                 tags                   = itags,
                 labeltype              = ilabeltype,
                 bastags                = ibastags,
                 contentid              = icontentid,
                 SOURCEDIRECTORS        = idirectors
           where c2code = icode;
        elsif isysid = 'u' then
          update credb.ws_mergedmedia
             set json_status = '0',
                 updatetime  = to_char(sysdate, 'yyyymmddhh24miss'),
                 updater     = 'prot',
                 syncflagu   = '2',
                 uoptags     = '',
                 status      = substr(istatus3, 1, 2) || '9' ||
                               substr(istatus3, 4, 3),
                 --
                 languages              = ilanguages,
                 countries              = icountries,
                 vspid                  = ivspid,
                 genres                 = igenres,
                 searchname             = iTITLE_SEARCH_NAME,
                 licensingwindowstart_U = ilicensingwindowstart,
                 licensingwindowend_U   = ilicensingwindowend,
                 DIRECTORS              = idirectors,
                 CASTS                  = icasts,
                 compere                = icompere,
                 SOURCECASTS            = icasts,
                 year                   = iyear,
                 tags                   = itags,
                 labeltype              = ilabeltype,
                 bastags                = ibastags,
                 contentid              = icontentid,
                 SOURCEDIRECTORS        = idirectors
           where c2code = icode;
        elsif isysid = 'a' then
          update credb.ws_mergedmedia
             set json_status = '0',
                 updatetime  = to_char(sysdate, 'yyyymmddhh24miss'),
                 updater     = 'prot',
                 syncflagu   = '2',
                 uoptags     = '',
                 status      = substr(istatus3, 1, 3) || '9' ||
                               substr(istatus3, 5, 2),
                 --
                 languages              = ilanguages,
                 countries              = icountries,
                 vspid                  = ivspid,
                 genres                 = igenres,
                 searchname             = iTITLE_SEARCH_NAME,
                 licensingwindowstart_A = ilicensingwindowstart,
                 licensingwindowend_A   = ilicensingwindowend,
                 DIRECTORS              = idirectors,
                 CASTS                  = icasts,
                 compere                = icompere,
                 year                   = iyear,
                 tags                   = itags,
                 labeltype              = ilabeltype,
                 bastags                = ibastags,
                 SOURCECASTS            = icasts,
                 contentid              = icontentid,
                 SOURCEDIRECTORS        = idirectors
           where c2code = icode;
        elsif isysid = 'b' then
          update credb.ws_mergedmedia
             set json_status = '0',
                 updatetime  = to_char(sysdate, 'yyyymmddhh24miss'),
                 updater     = 'prot',
                 syncflagu   = '2',
                 uoptags     = '',
                 status      = substr(istatus3, 1, 4) || '9' ||
                               substr(istatus3, 6, 1),
                 --
                 languages              = ilanguages,
                 countries              = icountries,
                 vspid                  = ivspid,
                 genres                 = igenres,
                 searchname             = iTITLE_SEARCH_NAME,
                 licensingwindowstart_B = ilicensingwindowstart,
                 licensingwindowend_B   = ilicensingwindowend,
                 DIRECTORS              = idirectors,
                 CASTS                  = icasts,
                 compere                = icompere,
                 year                   = iyear,
                 tags                   = itags,
                 labeltype              = ilabeltype,
                 bastags                = ibastags,
                 SOURCECASTS            = icasts,
                 contentid              = icontentid,
                 SOURCEDIRECTORS        = idirectors
           where c2code = icode;
        elsif isysid = 'c' then
          update credb.ws_mergedmedia
             set json_status = '0',
                 updatetime  = to_char(sysdate, 'yyyymmddhh24miss'),
                 updater     = 'prot',
                 syncflagu   = '2',
                 uoptags     = '',
                 status      = substr(istatus3, 1, 5) || '9',
                 --
                 languages              = ilanguages,
                 countries              = icountries,
                 vspid                  = ivspid,
                 genres                 = igenres,
                 searchname             = iTITLE_SEARCH_NAME,
                 licensingwindowstart_C = ilicensingwindowstart,
                 licensingwindowend_C   = ilicensingwindowend,
                 DIRECTORS              = idirectors,
                 CASTS                  = icasts,
                 compere                = icompere,
                 year                   = iyear,
                 tags                   = itags,
                 labeltype              = ilabeltype,
                 bastags                = ibastags,
                 SOURCECASTS            = icasts,
                 contentid              = icontentid,
                 SOURCEDIRECTORS        = idirectors
           where c2code = icode;
        end if;
        insert into sp_operation_log
          (code, action, table_name, msg)
        values
          (iCODE, 'delete', 'programtag', 'succeed');
      elsif icount1 = 0 then
        null;
      end if;
    end if;
  end if;
  commit;
exception
  when others then
    dbms_output.put_line('oracle error code:' || SQLCODE ||
                         'error message:' || substr(SQLERRM, 1, 100));
    null;
end;
/
