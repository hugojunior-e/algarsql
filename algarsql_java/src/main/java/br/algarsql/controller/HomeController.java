package br.algarsql.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import br.algarsql.utils.Ldap;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;

@Controller
public class HomeController {

    // ==========================================================================================
    // Home e Login
    // ==========================================================================================

    @GetMapping("/")
    public String home(HttpServletRequest request, HttpSession session, Model model) {
        Object o = session.getAttribute("username");
        if ( o == null ) {
            return "redirect:/login";
        }
        String username = o.toString();
        
        model.addAttribute("login", username);

        String cs = (String) session.getAttribute("theme");
        String edt = cs.contains("plsql") ? "vs" : "vs-dark";
        model.addAttribute("edt", edt);
        model.addAttribute("css", cs);

        return "index";
    }

    // ==========================================================================================
    //
    // ==========================================================================================

    @GetMapping("/login")
    public String loginPage() {
        return "login";
    }


    @PostMapping("/validadeLogin")
    public String validadeLogin(@RequestParam String username, @RequestParam String password,
            @RequestParam(required = false) String theme, HttpServletRequest request, HttpSession session) {

        boolean ok = Ldap.ldapLogin(username, password);

        if (ok) {
            session.setAttribute("username", username);
            session.setAttribute("theme", theme);
            return "redirect:/";
        }

        return "redirect:/error";
    }

    // ==========================================================================================
    //
    // ==========================================================================================

    @GetMapping("/{page}")
    public String renderPage(@PathVariable String page) {
        return page;
    }
}
