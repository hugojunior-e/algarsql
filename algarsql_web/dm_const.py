## ==============================================================================================
## Constantes
## ==============================================================================================

C_APP_VERSION         = "AlgarSQL 2.3"
C_SQL_SELECT          = "user_exec.pc_exec_dml.pr_exec_select"
C_SQL_EXEC            = "user_exec.pc_exec_dml.pr_exec_dml"

C_SQL_ALL_TAB_COLUMNS = """
  SELECT COLUMN_NAME, OWNER , lpad( row_number() over(order by OWNER, COLUMN_ID) , 10,'0')
    FROM ALL_TAB_COLUMNS 
   WHERE TABLE_NAME = upper('%s') 
   ORDER BY OWNER, COLUMN_ID"""


C_SQL_ALL_TABLES_COLUMNS           = """
  SELECT TABLE_NAME, OWNER, lpad( row_number() over(order by OWNER, TABLE_NAME) , 10,'0')  
    FROM ALL_TABLES 
   WHERE OWNER = upper('%s') ORDER BY 1
"""

C_SQL_ALL_TABLES           = "SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = upper('%s') ORDER BY 1"


C_SQL_TABLE_DESCRIBE_PROP  = "SELECT * FROM ALL_TABLES WHERE TABLE_NAME = upper( '%s' ) ORDER BY OWNER"

C_SQL_TABLE_DESCRIBE_COLS  = """
SELECT t.column_name,
       t.data_type,
       t.data_length,
       t.nullable,
       t.table_name,
       t.owner,
       c.comments AS column_description
  FROM all_tab_columns t
  LEFT JOIN all_col_comments c ON ( c.owner = t.owner AND c.table_name = t.table_name AND c.column_name = t.column_name )
 WHERE t.table_name = UPPER('%s')
 ORDER BY t.owner, t.column_id
"""

C_SQL_TABLE_INDEXES        = """
select (SELECT decode(UNIQUENESS,'UNIQUE','UNIQUE','NORMAL') FROM ALL_INDEXES WHERE OWNER = vw.table_owner and INDEX_NAME = vw.INDEX_NAME) INDEX_TYPE,
       vw.*
  from (
          SELECT index_name,table_owner,
                 RTRIM(XMLAGG(XMLELEMENT(e, column_name || ',') ORDER BY column_position).EXTRACT('//text()'), ',') campos
            FROM all_ind_columns t
            WHERE table_name = UPPER('%s')
            --AND table_owner = 
            GROUP BY index_name,table_owner
       ) vw
 order by 1      
"""

C_SQL_FIND_OBJECT          = """
  SELECT owner, 
         object_name, 
         object_type, 
         CREATED,
         LAST_DDL_TIME, 
         STATUS 
    FROM ALL_OBJECTS 
   WHERE OBJECT_NAME LIKE upper('%s') 
     AND OBJECT_TYPE NOT IN ('SYNONYM') 
   order by owner,object_type,object_name 
"""

C_SQL_ALL_ERRORS           = "SELECT ATTRIBUTE, LINE, TEXT  FROM ALL_ERRORS  WHERE OWNER = upper( '%s' ) AND NAME = upper( '%s' )  ORDER BY SEQUENCE"
C_SQL_START                = "begin dbms_output.enable(100000); DBMS_APPLICATION_INFO.SET_CLIENT_INFO('ALGAR SQL'); end;"

C_SQL_DML                  = """
begin
  :ddl := user_exec.PC_EXEC_DML.f_get_ddl( '<1>' , '<2>', '<3>') 
            ||  
          case when '<1>'  = 'PACKAGE' then
                '<end_package_spec>' || user_exec.PC_EXEC_DML.f_get_ddl( 'PACKAGE BODY', '<2>', '<3>') 
          end;
end;
"""

C_SQL_PROCEDURE_REFCURSOR = """
  PROCEDURE print_refcursor(p_cursor IN OUT SYS_REFCURSOR) IS
      v_cursor_id   NUMBER;
      v_col_count   NUMBER;
      v_desc_tab    DBMS_SQL.DESC_TAB;
      v_value       VARCHAR2(4000);
      v_status      NUMBER;
  BEGIN
      IF p_cursor%ISOPEN THEN
          v_cursor_id := DBMS_SQL.TO_CURSOR_NUMBER(p_cursor);
      ELSE
          DBMS_OUTPUT.PUT_LINE('Cursor not Opened!');
          RETURN;
      END IF;
      DBMS_SQL.DESCRIBE_COLUMNS(v_cursor_id, v_col_count, v_desc_tab);
      FOR i IN 1 .. v_col_count LOOP
          DBMS_SQL.DEFINE_COLUMN(v_cursor_id, i, v_value, 4000);
      END LOOP;
      LOOP
          v_status := DBMS_SQL.FETCH_ROWS(v_cursor_id);
          EXIT WHEN v_status = 0;

          FOR i IN 1 .. v_col_count LOOP
              DBMS_SQL.COLUMN_VALUE(v_cursor_id, i, v_value);
              DBMS_OUTPUT.PUT(v_value || ' | ');
          END LOOP;

          DBMS_OUTPUT.NEW_LINE;
      END LOOP;
      DBMS_SQL.CLOSE_CURSOR(v_cursor_id);
  END;
"""


C_SQL_PROCEDURE_ARGS = """
      select argument_name,
             position,
             data_type,
             in_out,
             owner
        from all_arguments
       where owner like '%s'
         and object_name   = '%s'
         and nvl(package_name,'-') = '%s'
         and argument_name is not null
        order by position
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
                  and type like REPLACE( trim(replace(v_type,'BODY','')) , 'PACKAGE', 'PACKAGE%' )
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
    SELECT OWNER || '|' || OBJECT_TYPE || '|' || OBJECT_NAME
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

C_SQL_EXPLAIN = "SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY())"""

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