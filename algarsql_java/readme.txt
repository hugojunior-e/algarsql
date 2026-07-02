
import java.io.File;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class TempFileCleaner {

    @Scheduled(fixedDelay = 60000) // a cada 60 segundos
    @Scheduled(cron = "0 0 0 * * *")
    public void limparArquivos() {

        File pasta = new File("/tmp");

        for (File f : pasta.listFiles()) {

            if (f.getName().endsWith(".db")) {
                f.delete();
            }
        }
    }
}