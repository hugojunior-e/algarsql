package br.algarsql.controller;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
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

    @RequestMapping(value = "/config_tnsnames", method = {RequestMethod.GET, RequestMethod.POST})
    public String configTnsnames() {
        String fp = System.getenv().getOrDefault("TNS_ADMIN", "-");
        String caminho = Paths.get(fp, "tnsnames.ora").toString();
        List<String> results = new ArrayList<>();

        results.add("File " + caminho + " not found.");
        File file = new File(caminho);

        if (file.exists()) {
            try {

                String content = Files.readString(file.toPath());
                // ---------------------------------------------------------
                // Remove comentários
                // ---------------------------------------------------------

                content = content.replaceAll("#.*", "");

                // ---------------------------------------------------------
                // Junta tudo em uma linha
                // ---------------------------------------------------------

                content = content.replaceAll("\\s+", " ");
                content = content.trim().replace(" ", "");

                // ---------------------------------------------------------
                // Regex
                // ---------------------------------------------------------

                Pattern pattern = Pattern.compile(
                        "(\\w+)\\s*=\\s*\\(DESCRIPTION=.*?" + "HOST\\s*=\\s*([^)]+).*?"
                                + "PORT\\s*=\\s*(\\d+).*?"
                                + "(SERVICE_NAME|SID)\\s*=\\s*([^)]+).*?\\)",
                        Pattern.CASE_INSENSITIVE);

                Matcher matcher = pattern.matcher(content);

                results = new ArrayList<>();

                while (matcher.find()) {

                    String alias = matcher.group(1);
                    String host = matcher.group(2);
                    String port = matcher.group(3);
                    String service = matcher.group(5);

                    String formatted =
                            String.format("%-35s | %s:%s/%s", alias, host, port, service);

                    results.add(formatted);
                }

            } catch (Exception e) {
                results = new ArrayList<>();
                results.add(e.getMessage());
            }
        }
        return String.join("\n", results);
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
        ret.put("tnsSaved", Utils.configValue("tnsSaved", null, u).toString());
        ret.put("tns", Utils.configValue("tns", null, u).toString());
        ret.put("oracle_home", System.getenv().getOrDefault("ORACLE_HOME", "").toString());
        return ret;
    }


    // ==========================================================================================
    //
    // ==========================================================================================

    @RequestMapping(value = "/config_save", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> configSave(HttpServletResponse response,HttpServletRequest request,HttpSession session, @RequestParam String tnsSaved,
            @RequestParam String tns) throws Exception {
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
}
