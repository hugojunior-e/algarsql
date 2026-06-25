package br.algarsql.controller;

import java.util.HashMap;
import java.util.Map;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import br.algarsql.utils.DATABASE;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;

@RestController
public class ParallelProcessController {
 
        @RequestMapping(value = "/th_status", method = {RequestMethod.GET, RequestMethod.POST})
        public Map<String, Object> getProcessStatus(HttpServletRequest request,HttpSession session) {
            String xTabId = request.getHeader("X-Tab-ID");
            DATABASE db = (DATABASE) session.getAttribute(xTabId);

            Map<String, Object> ret = new HashMap<>();
            ret.put("status_code", db.status_code_parallel);
            ret.put("status_msg", db.status_msg);
            return ret;
        }

        @RequestMapping(value = "/th_stop", method = {RequestMethod.GET, RequestMethod.POST})
        public Map<String, Object> stopProcess(HttpServletRequest request,HttpSession session) {
            String xTabId = request.getHeader("X-Tab-ID");
            DATABASE db = (DATABASE) session.getAttribute(xTabId);
            db.STOP();
            Map<String, Object> ret = new HashMap<>();
            ret.put("status_code", db.status_code_parallel);
            ret.put("status_msg", db.status_msg);
            return ret;
        }        
            
}
