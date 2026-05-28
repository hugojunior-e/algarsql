package br.algarsql.utils;

import javax.naming.Context;
import javax.naming.NamingEnumeration;
import javax.naming.directory.*;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.List;

public class Ldap {

    public static boolean ldapCheck(String adServidor, String usuarioDn, String senha) {
        try {
            Hashtable<String, String> env = new Hashtable<>();
            env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
            env.put(Context.PROVIDER_URL, "ldap://" + adServidor + ":389");
            env.put(Context.SECURITY_AUTHENTICATION, "simple");
            env.put(Context.SECURITY_PRINCIPAL, usuarioDn);
            env.put(Context.SECURITY_CREDENTIALS, senha);
            DirContext ctx = new InitialDirContext(env);
            ctx.close();
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    // =========================================================================
    // ldap_get_groups
    // =========================================================================

    public static List<String> ldapGetGroups(String adServidor, String usuarioDn, String senha) {
        List<String> grupos = new ArrayList<>();
        try {
            Hashtable<String, String> env = new Hashtable<>();
            env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
            env.put(Context.PROVIDER_URL, "ldap://" + adServidor + ":389");
            env.put(Context.SECURITY_AUTHENTICATION, "simple");
            env.put(Context.SECURITY_PRINCIPAL, usuarioDn);
            env.put(Context.SECURITY_CREDENTIALS, senha);
            DirContext ctx = new InitialDirContext(env);
            SearchControls controls = new SearchControls();
            controls.setSearchScope(SearchControls.SUBTREE_SCOPE);
            controls.setReturningAttributes(new String[] {"memberOf"});
            NamingEnumeration<SearchResult> results =
                    ctx.search(usuarioDn, "(objectClass=person)", controls);
            while (results.hasMore()) {
                SearchResult result = results.next();
                Attributes attrs = result.getAttributes();
                Attribute memberOf = attrs.get("memberOf");
                if (memberOf != null) {
                    NamingEnumeration<?> groups = memberOf.getAll();
                    while (groups.hasMore()) {
                        grupos.add(groups.next().toString());
                    }
                }
            }
            ctx.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return grupos;
    }

    // =========================================================================
    // ldap_login
    // =========================================================================

    public static boolean ldapLogin(String username, String password) {
        String adServidor = "10.51.47.125";
        String[] domains = {"associado", "terceiro", "temporario", "estagiario"};
        for (String domain : domains) {
            String userDn =
                    "CN=" + username + ",ou=" + domain + ",cn=Users" + ",dc=network" + ",dc=ctbc";
            boolean ok = ldapCheck(adServidor, userDn, password);
            if (ok) {
               // List<String> grupos =
                // ldapGetGroups(
                // adServidor,
                // userDn,
                // password
                // );
                return true;
            }
        }
        return false;
    }
}
