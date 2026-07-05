package br.algarsql.controller;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import br.algarsql.utils.Constants;
import br.algarsql.utils.Utils;

@RestController
public class ConfigController {

    // ==========================================================================================
    //
    // ==========================================================================================

    @RequestMapping(value = "/config_get_tnsnames", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> configGetTnsnames(HttpServletResponse response,HttpServletRequest request, HttpSession session) throws Exception {
        Map<String, Object> ret = new HashMap<>();

        Object o = session.getAttribute("username");
        if ( o == null ) {
            response.setStatus(401);
            ret.put("redirect", Constants.PAGE_LOGIN);
            return ret;
        }
        
        String newCode = Files.readString(Path.of( Constants.WORKDIR + "/tnsnames.ora"));
        
        ret.put("tnsnames", newCode);
        return ret;
    }
    // ==========================================================================================
    //
    // ==========================================================================================

    @RequestMapping(value = "/format_plsql", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> formatPlsql(HttpServletResponse response,HttpServletRequest request, HttpSession session) throws Exception {
        Map<String, Object> ret = new HashMap<>();

        Object o = session.getAttribute("username");
        if ( o == null ) {
            response.setStatus(401);
            ret.put("redirect", Constants.PAGE_LOGIN);
            return ret;
        }
        String c = request.getParameter("code");
        String newCode = Utils.formatCode(c);

        
        ret.put("newcode", newCode);
        return ret;
    }


    // ==========================================================================================
    //
    // ==========================================================================================

    @RequestMapping(value = "/config_get", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> configGet(HttpServletResponse response,HttpServletRequest request, HttpSession session) throws Exception {
        Map<String, Object> ret = new HashMap<>();
        Object o = session.getAttribute("username");
        if ( o == null ) {
            response.setStatus(401);
            ret.put("redirect", Constants.PAGE_LOGIN);
            return ret;
        }

        String u = o.toString();
        String monacoThemeDefault = Utils.configValue("monacoTheme", null, u).toString();
        if (monacoThemeDefault.length() == 0) {
            monacoThemeDefault = "style-dark.css";
        };

        String bip = Utils.configValue("bip", null, u).toString();
        if (bip.length() == 0) {
            bip = "1";
        };
        ret.put("tnsSaved", Utils.configValue("tnsSaved", null, u).toString());
        ret.put("tns", Utils.configValue("tns", null, u).toString());
        ret.put("bip", bip);
        ret.put("monacoTheme", monacoThemeDefault);
        return ret;
    }


    // ==========================================================================================
    //
    // ==========================================================================================

    @RequestMapping(value = "/config_save", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> configSave(HttpServletResponse response,HttpServletRequest request,HttpSession session, @RequestParam String tnsSaved,
            @RequestParam String tns, @RequestParam String monacoTheme,  @RequestParam String bip ) throws Exception {
        Map<String, Object> ret = new HashMap<>();
        Object o = session.getAttribute("username");
        if ( o == null ) {
            response.setStatus(401);
            ret.put("redirect", Constants.PAGE_LOGIN);
            return ret;
        }
        String u = o.toString();


        Utils.configSave("tnsSaved", tnsSaved, "CONFIG", u);
        Utils.configSave("tns", tns, "CONFIG", u);
        Utils.configSave("monacoTheme", monacoTheme, "CONFIG", u);
        Utils.configSave("bip", bip, "CONFIG", u);
        ret.put("status_msg", "Configuration saved successfully.");
    
        return ret;
    }

    // ==========================================================================================
    //
    // ==========================================================================================

    @RequestMapping(value = "/config_recall", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> configRecall(HttpServletResponse response,HttpServletRequest request,HttpSession session,
            @RequestParam(defaultValue = "%") String text,
            @RequestParam(defaultValue = "%") String database) throws Exception {

        Map<String, Object> ret = new HashMap<>();
        Object o = session.getAttribute("username");
        if ( o == null ) {
            response.setStatus(401);
            ret.put("redirect", Constants.PAGE_LOGIN);
            return ret;
        }
        String u = o.toString();


        Object dadosBrutosObj = Utils.configValue("SQL_HISTORY", new String[] {text, database}, u);
        List<Map<String, Object>> dados = new ArrayList<>();

        if (dadosBrutosObj instanceof List<?>) {

            List<?> lista = (List<?>) dadosBrutosObj;

            for (Object item : lista) {
                if (item instanceof Map<?, ?> row) {
                    Map<String, Object> novo = new LinkedHashMap<>();
                    novo.put("Data", row.get("dt"));
                    novo.put("Dbname", row.get("dbname"));
                    novo.put("SQL", row.get("info"));
                    dados.add(novo);
                }
            }
        }
        ret.put("data", dados);
        ret.put("columns", List.of("Data", "Dbname", "SQL"));
        ret.put("columns_types", List.of("DATETIME", "STRING", "STRING"));
        return ret;
    }



// ==========================================================================================
    //
    // ==========================================================================================

    @SuppressWarnings("unchecked")
    @RequestMapping(value = "/config_workdata_load", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> configWorkdataLoad(HttpServletResponse response,HttpServletRequest request,HttpSession session) throws Exception {

        Map<String, Object> ret = new HashMap<>();
        Object o = session.getAttribute("username");
        if ( o == null ) {
            response.setStatus(401);
            ret.put("redirect", Constants.PAGE_LOGIN);
            return ret;
        }
        String u = o.toString();


        Object dadosBrutosObj = Utils.configValue("SQL_WORKDATA_LOAD", new String[] {}, u);
        Map<String, Object> dados = (Map<String, Object>) dadosBrutosObj;

        ret.put("data", dados.get("data"));
        ret.put("columns", dados.get("columns"));
        ret.put("columns_types", dados.get("columns_types"));
        return ret;
    }
    
}
