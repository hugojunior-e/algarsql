package br.algarsql.utils;

import org.springframework.context.ApplicationContext;

public class Constants {

  public static ApplicationContext applicationContext;

  public static final String PAGE_LOGIN = "/login";
  public static final String FARMPRD_USR = "ALGARSQLAPP";
  public static final String FARMPRD_PWD = "P7RT6L#26sql";
  public static final String FARMPRD_DSN = "exa07-scan-prd.network.ctbc:1521/FARMPRD";
  public static final String WORKDIR = "/algarsql";

  // =========================================================================================
  // SQL_ORACLE
  // =========================================================================================

  public static final String C_ORACLE_KILL_SESSIONS = """
          begin
          for cx in (  select * from algarsqlapp.vw_kill_session
                          where upper(username) LIKE upper('<1>')
                      )
          loop
              execute immediate cx.k;
          end loop;
          end;
      """;

  public static final String C_ORACLE_CHANGE_PASSWORD = """
                DECLARE
                  P_Nm_Usuario    VARCHAR2(128)  := '<1>';
                  P_Senha_Usuario VARCHAR2(4000) := '<2>';
                  P_Msg_Retorno   VARCHAR2(2048) := 'SUCESSO';
                  v_user_banco    VARCHAR2(128);
                  v_qtd           number;
                BEGIN
                    PKG_RESET_SENHA_USUARIO.PRO_RESET_SENHA ( upper(P_Nm_Usuario) , P_Senha_Usuario , P_Msg_Retorno );

                    if (P_Msg_Retorno LIKE '%ERRO%' or upper(P_Msg_Retorno) like '%EXISTE%'  ) then
                        raise_application_error(-20003, P_Msg_Retorno );
                    end if;

                    -- DESBLOQUEANDO USUARIO
                    PKG_RESET_SENHA_USUARIO.PRO_UNLOCK_USUARIO (upper(v_user_banco), P_Msg_Retorno );


                    if (P_Msg_Retorno LIKE '%ERRO%') then
                        raise_application_error(-20004, P_Msg_Retorno );
                    end if;
                END;
      """;

  public static final String C_CHANGE_PASSWORD_GET_USER_FOUND = """
            SELECT * FROM
            (
                    SELECT --+ parallel
                        distinct SUBSTR(tb_recurso.name,18) data_base, tb_conta.accountIdentifier
                    FROM blazonadm.MembershipEntitlement tb_membrododireito
                    INNER JOIN blazonadm.Account tb_conta                             ON tb_membrododireito.account_id = tb_conta.id
                    INNER JOIN blazonadm.b_Resource tb_recurso                          ON tb_conta.resource_id = tb_recurso.id
                    INNER JOIN blazonadm.B_USER tb_user                          ON tb_user.id = tb_conta.user_id
                    WHERE 1 = 1
                    AND upper(tb_recurso.name) LIKE '%BANCO DE DADOS%PRD' -- NOME DO RECURSO
                    and upper( tb_user.USERNAME ) = upper('<1>')  --entre aq com o usuario de rede ( logado no app algarsql )

                    UNION

                    SELECT --+ parallel
                    'CMPRD' data_base, tb_conta.accountIdentifier
                    FROM blazonadm.MembershipEntitlement tb_membrododireito
                    INNER JOIN blazonadm.Account tb_conta                             ON tb_membrododireito.account_id = tb_conta.id
                    INNER JOIN blazonadm.b_Resource tb_recurso                          ON tb_conta.resource_id = tb_recurso.id
                    INNER JOIN blazonadm.B_USER tb_user                          ON tb_user.id = tb_conta.user_id
                    WHERE 1 = 1
                    AND upper(tb_recurso.name) = 'CONNECT MASTER' -- NOME DO RECURSO
                    and upper( tb_user.USERNAME ) = upper('<1>') --entre aq com o usuario de rede ( logado no app algarsql )

            )
            WHERE DATA_BASE IN (
                    select NAME
                    from deployadm.T_CFG_BASE tcb
                    START WITH tcb.NAME = '<2>'  --ENTRE AQ COM A BASE QUE QUER TROCAR A SENHA
                    CONNECT BY PRIOR ID = BASE_DEP_ID
            )
      """;

}
