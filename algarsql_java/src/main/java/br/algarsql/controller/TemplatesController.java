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

        if ( request.getSession(false) == null ) {
            response.sendRedirect(Constants.PAGE_LOGIN);
            return null;
        }
        String username = (String) session.getAttribute("username");

        Map<String, Object> ret = new HashMap<>();

        String action = request.getParameter("action");


        try {
            if (username == null) {
                response.sendRedirect(Constants.PAGE_LOGIN);
                return null;
            }        

            // ---------------------------------------------------------
            // SAVE TEMPLATE
            // ---------------------------------------------------------
            if ("save".equals(action)) {

                String newName = request.getParameter("name");
                String newValue = request.getParameter("value");
                String oldName = request.getParameter("old_name");

                if (!newName.contains("|")) {
                    newName = "root|" + newName;
                }

                Map<String, Object> tagValue = new HashMap<>();
                tagValue.put("node", newName);
                tagValue.put("info", newValue);

                Utils.configSave(oldName, tagValue, "SQL_TEMPLATES", username);

                ret.put("status_msg", "Success");
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
