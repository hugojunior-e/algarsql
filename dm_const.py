## ==============================================================================================
## Constantes
## ==============================================================================================

C_EDITOR_SQL         = 0
C_EDITOR_TXT         = 1
C_EDITOR_PYC         = 2


C_APP_VERSION         = "AlgarSQL 2.3"
C_SQL_SELECT          = "user_exec.pc_exec_dml.pr_exec_select"
C_SQL_EXEC            = "user_exec.pc_exec_dml.pr_exec_dml"
C_SQL_ALL_TAB_COLUMNS = "SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = upper('%s') ORDER BY OWNER, COLUMN_ID"
C_SQL_ALL_TABLES      = "SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = upper('%s') ORDER BY 1"
C_SQL_PROPERTIES      = "SELECT * FROM ALL_TABLES WHERE TABLE_NAME = '%s' ORDER BY OWNER"
C_SQL_DESCRIBE        = "SELECT column_name, data_type, data_length, nullable, table_name, owner FROM all_tab_columns t where table_name = '%s'  order by owner, t.column_id"
C_SQL_FIND_OBJECT     = "SELECT * FROM ALL_OBJECTS WHERE OBJECT_NAME LIKE upper('%s') AND OBJECT_TYPE IN (%s)"
C_SQL_ALL_ERRORS      = "SELECT ATTRIBUTE, LINE, TEXT  FROM ALL_ERRORS  WHERE OWNER = '%s' AND NAME = '%s'  ORDER BY SEQUENCE"
C_SQL_START           = "begin dbms_output.enable(100000); DBMS_APPLICATION_INFO.SET_CLIENT_INFO('ALGAR SQL'); end;"
C_SQL_ENABLE_WARN     = "ALTER SESSION SET PLSQL_WARNINGS='ENABLE:ALL'"

C_SQL_DML             = """
begin
  :ddl := user_exec.PC_EXEC_DML.f_get_ddl( '<1>' , '<2>', '<3>') 
            ||  
          case when '<1>'  = 'PACKAGE' then
                '<end_package_spec>' || user_exec.PC_EXEC_DML.f_get_ddl( 'PACKAGE BODY', '<2>', '<3>') 
          end;
end;
"""

C_SQL_DML_DIRECT      = """
declare
  v_type  varchar2(100) := '<1>';
  v_owner varchar2(100) := '<2>';
  v_name  varchar2(100) := '<3>';
  v_ret   clob;
  v_tipo  varchar2(32000);
begin
  dbms_lob.createtemporary(v_ret, true);
  
  if v_type not in ('TABLE', 'VIEW', 'MATERIALIZED VIEW') then
    dbms_lob.append(v_ret, 'CCRREEAATTEE OR REPLACE ');
    for cx in (select case when line = 1 and upper(text) not like '%' || upper(owner) || '.%' then
                             REGEXP_REPLACE(text,name, owner || '.' || name, 1, 0, 'i')
                           else
                             text
                      end text, 
                      line, 
                      type
                 from all_source
                where name = v_name
                  and type like replace(v_type,'PACKAGE','PACKAGE%')
                  and owner = v_owner
                order by type, line)
    loop
      if (cx.line = 1 and cx.type = 'PACKAGE BODY') then
        dbms_lob.append(v_ret, '<end_package_spec>CCRREEAATTEE OR REPLACE ');
      end if;
      dbms_lob.append(v_ret, cx.text);
    end loop;
  end if;

  if v_type = 'TABLE' then
    dbms_lob.append(v_ret, 'CCRREEAATTEE TABLE ' || v_owner || '.' || v_name || '(' || chr(10));
    for cx in (
                SELECT '  '
                       || RPAD(COLUMN_NAME,40,' ') || DATA_TYPE 
                       || (
                            CASE WHEN DATA_TYPE NOT IN ('DATE','CLOB','BLOB') THEN
                            '(' || DATA_LENGTH || nvl2(data_precision, ',' || data_precision, '') || ')'
                            END
                          ) 
                       ||' ' || (CASE WHEN NULLABLE = 'N' THEN 'NOT NULL' END)   text,
                       DATA_DEFAULT,
                       case when COLUMN_ID = (max(COLUMN_ID) over()) then '' else ',' end fim
                  FROM ALL_TAB_COLUMNS
                 WHERE OWNER = v_owner
                   AND TABLE_NAME = v_name
                ORDER BY COLUMN_ID               
              )
    loop
      v_tipo := CX.DATA_DEFAULT;
      if v_tipo is not null then
        v_tipo := ' DEFAULT ' || trim(v_tipo);
      end if;

      dbms_lob.append(v_ret, cx.text || v_tipo || cx.fim || chr(10));
    end loop;
    dbms_lob.append(v_ret, ');' || chr(10));
  
    FOR cx IN (SELECT index_name,
                      RTRIM(XMLAGG(XMLELEMENT(e, column_name || ',') ORDER BY column_position).EXTRACT('//text()'), ',') campos
                 FROM all_ind_columns t
                WHERE table_name = v_name
                  AND table_owner = v_owner
                GROUP BY index_name)
    LOOP
      SELECT UNIQUENESS
        INTO v_tipo
        FROM ALL_INDEXES
       WHERE OWNER = v_owner
         AND INDEX_NAME = CX.INDEX_NAME;
    
      dbms_lob.append(v_ret,'CCRREEAATTEE ' || (CASE WHEN v_tipo = 'UNIQUE' THEN v_tIpo END) || ' INDEX ' || v_owner || '.' || cx.index_name || ' ON ' || v_owner || '.' || v_name || '(' || cx.campos || ');' || CHR(10));
    END LOOP;
  
  end if;

  if v_type like '%VIEW%' then
    SELECT A INTO V_TIPO FROM
    (
            SELECT TEXT A FROM ALL_VIEWS WHERE OWNER = v_owner AND VIEW_NAME = v_name
            UNION ALL
            SELECT QUERY A FROM ALL_MVIEWS WHERE OWNER = v_owner AND MVIEW_NAME = v_name
    );        
  
    dbms_lob.append(v_ret, 'CCRREEAATTEE OR REPLACE ' || v_type || ' ' || v_owner || '.' || v_name || ' AS ' || chr(10));
    dbms_lob.append(v_ret, V_TIPO);
  end if;
  :ddl := v_ret;
end;
"""

C_SQL_TREE = """
    SELECT OWNER,         
        OBJECT_TYPE,   
        OBJECT_NAME,
        STATUS  
    FROM ALL_OBJECTS    
    WHERE OBJECT_TYPE IN ('PROCEDURE', 'TABLE', 'VIEW', 'FUNCTION', 'TRIGGER', 'MATERIALIZED VIEW', 'PACKAGE', 'TRIGGER')
    AND OWNER not in ( 'SYSTEM', 'SYS',
            'ORDDATA', 'FLOWS_FILES', 'APEX_030200', 'APEX_040200', 'APEX_PUBLIC_USER', 'OLAPSYS', 'QUEST', 'OUTLN', 'RMAN', 'XDB', 'C##CLOUD$SERVICE', 'ANONYMOUS',
            'APPQOSSYS', 'AUDSYS', 'CTXSYS', 'DBSFWUSER', 'DBSNMP', 'DIP', 'DMSYS', 'DVF', 'DVSYS', 'DUMMY', 'EXFSYS', 'GGSYS', 'GSMADMIN_INTERNAL', 'GSMCATUSER', 'GSMUSER', 'LBACSYS',
            'MDDATA', 'MDSYS', 'MGMT_VIEW', 'OJVMSYS', 'OLAPSYS', 'ORACLE_OCM', 'ORDDATA', 'ORDPLUGINS', 'ORDSYS', 'OUTLN', 'REMOTE_SCHEDULER_AGENT', 'SI_INFORMTN_SCHEMA', 'SCOTT',
            'SYS$UMF', 'SYSBACKUP', 'SYSDG', 'SYSKM', 'SYSMAN', 'SYSRAC', 'TSMSYS', 'WMSYS', 'XDB', 'XS$NULL', 'OWBSYSOWBSYS_AUDIT', 'SPATIAL_WFS_ADMIN_USR', 'SPATIAL_CSW_ADMIN_USR',
            'OWBSYS', 'OWBSYS_AUDIT', 'SPATIAL_WFS_ADMIN_USR', 'SPATIAL_CSW_ADMIN_USR')
    order by OWNER,OBJECT_TYPE,OBJECT_NAME
"""


C_SQL_RECOMPILE = """
    SELECT owner || '.' || object_name || '(' || object_type  || ')' obj,
           'ALTER ' 
           || DECODE(object_type,'PACKAGE BODY','PACKAGE', object_type) 
           || ' ' 
           || owner 
           || '.' || object_name 
           || ' COMPILE ' 
           || DECODE(object_type,'PACKAGE BODY','BODY', '') cmd
    FROM all_objects
    WHERE status != 'VALID'
    ORDER BY DECODE(object_type,'PACKAGE',1,'PACKAGE BODY',2,2)
"""

C_SQL_SESSIONS_ALGAR = """
    SELECT  USERNAME || '(' || count(1) over (partition by username order by 1) || ')' username,
            STATUS|| '(' || count(1) over (partition by username, status order by 1) || ')' status,
            SID,
            SERIAL#,
            LOGON_TIME,
            OSUSER,
            MACHINE,
            PROGRAM,
            SQL_ID,
            CLIENT_INFO,
            SQL_FULLTEXT
    FROM <TABELA> 
   WHERE STATUS LIKE '<WHERE>'
ORDER BY USERNAME, STATUS, LOGON_TIME    
"""

C_SQL_SESSIONS_ORA = """
SELECT x.username || '(' || count(1) over (partition by x.username order by 1) || ')' username,
       x.STATUS|| '(' || count(1) over (partition by x.username, x.status order by 1) || ')' status,
       x.sid,
       x.serial#,
       x.logon_time,
       x.osuser,
       x.machine,
       x.program,
       x.sql_id,
       x.client_info,
       sql_fulltext
FROM   sys.v_$sqlarea sqlarea, sys.v_$session x
WHERE  x.sql_hash_value = sqlarea.hash_value(+)
   and x.sql_address = sqlarea.address(+)
   and x.username is not null
   AND x.status LIKE '<WHERE>'
ORDER BY x.username, x.status, X.LOGON_TIME    
"""

C_SQL_EXPLAIN = """
  select id,
         nvl(parent_id, -1) parent_id,
         operation || ' ' || decode(id, 0, optimizer, options),
         object_owner,
         object_name,
         object_type,
         to_char(cost),
         to_char(cardinality),
         to_char(bytes)
    from plan_table
   order by id
"""

C_SQL_DBMS = """
    declare                                                   
        l_data_qtd NUMBER          := 32000;                                      
        p_ret      varchar2(32000) := '';  
        lines      DBMS_OUTPUT.CHARARR;                   
    BEGIN                                                     
        DBMS_OUTPUT.get_lines(lines, l_data_qtd);  
        FOR x IN lines.FIRST .. lines.LAST
        LOOP
          p_ret := p_ret || lines(x) || chr(10);
        END LOOP;         
        :retorno := p_ret;                                      
    END;
"""