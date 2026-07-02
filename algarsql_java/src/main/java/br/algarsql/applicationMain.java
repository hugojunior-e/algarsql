package br.algarsql;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.context.ApplicationContextAware;
//import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.context.ApplicationContext;

@SpringBootApplication(scanBasePackages = "br.algarsql",  exclude = {DataSourceAutoConfiguration.class})
//@EnableScheduling
public class applicationMain implements ApplicationContextAware {

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) {
        br.algarsql.utils.Constants.applicationContext = applicationContext;
    }

    public static void main(String[] args) {
        SpringApplication.run(applicationMain.class, args);
    }
}

