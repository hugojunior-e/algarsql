package br.algarsql.controller;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import br.algarsql.utils.Constants;
import br.algarsql.utils.Utils;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class TemplatesController {

    // ==========================================================================================
    //
    // ==========================================================================================


    @RequestMapping(value = "/template", method = {RequestMethod.GET, RequestMethod.POST})
    public Map<String, Object> templateActions(HttpServletResponse response, HttpServletRequest request, HttpSession session) throws Exception {
        Map<String, Object> ret = new HashMap<>();

        Object o = session.getAttribute("username");
        if ( o == null ) {
            response.setStatus(401);
            ret.put("redirect", Constants.PAGE_LOGIN);
            return ret;
        }
        String username = o.toString();

        String action = request.getParameter("action");


        try {
            // ---------------------------------------------------------
            // SAVE TEMPLATE
            // ---------------------------------------------------------
            if ("save".equals(action)) {
                String name  = request.getParameter("name");
                String value = request.getParameter("value");
                Utils.configSave(name, value, "SQL_TEMPLATES.SAVE", username);
                ret.put("status_msg", "saved successfully");
                ret.put("status_code", 0);
                return ret;
            }

            // ---------------------------------------------------------
            // LOAD TEMPLATES
            // ---------------------------------------------------------
            else if ("load".equals(action)) {
                @SuppressWarnings("unchecked")
                List<Map<String, String>> list = (List<Map<String, String>>) Utils
                        .configValue("SQL_TEMPLATES", new String[] {"%"}, username);

                StringBuilder sb = new StringBuilder();
                for (Map<String, String> item : list) {
                    String value = item.get("node");
                    if (!value.contains("|")) {
                        value = "root|" + value;
                    }
                    sb.append(value).append("\n");
                }
                ret.put("templates", sb.toString().trim());
                ret.put("status_code", 0);
                return ret;
            }

            // ---------------------------------------------------------
            // OPEN TEMPLATE
            // ---------------------------------------------------------
            else if ("open".equals(action)) {
                String name = request.getParameter("name");
                @SuppressWarnings("unchecked")
                List<Map<String, String>> list = (List<Map<String, String>>) Utils
                        .configValue("SQL_TEMPLATES", new String[] {name}, username);

                if (list != null && !list.isEmpty()) {
                    ret.put("code", list.get(0).get("info"));
                } else {
                    ret.put("code", "Template not found.");
                }
                ret.put("status_code", 0);
                return ret;
            }
            else if ("delete".equals(action)) {
                String type = request.getParameter("type");
                String name = request.getParameter("name") + (type.equals("FILE") ? "" : "|%");
                Utils.configSave(name, null, "SQL_TEMPLATES.DEL", username);
                ret.put("status_msg", "successfully deleted");
                ret.put("status_code", 0);
                return ret;
            }
            else if ("rename".equals(action) || "moveto".equals(action)) {
                String type = request.getParameter("type");
                String name = request.getParameter("name") + (type.equals("FILE") ? "" : "|%");
                String newName = request.getParameter("new_name");
                Utils.configSave(name, newName, "SQL_TEMPLATES.RENAME", username);
                ret.put("status_msg", "rename".equals(action) ? "successfully renamed" : "successfully moved");
                ret.put("status_code", 0);
                return ret;
            }
            else if ("newfile".equals(action)) {
                String newName = request.getParameter("new_name");
                String value   = request.getParameter("value");
                Utils.configSave(newName, value, "SQL_TEMPLATES.NEW", username);
                ret.put("status_msg", "New file created successfully.");
                ret.put("status_code", 0);
                return ret;
            }            
           

            // ---------------------------------------------------------
            // INVALID ACTION
            // ---------------------------------------------------------
            ret.put("status_msg", "Invalid action");
            ret.put("status_code", 1);
            return ret;
        } catch (Exception e) {
            ret.put("status_msg", e.getMessage());
            ret.put("status_code", 1);
            return ret;
        }
    }
}
