/*
    ==========================================================================================------------------------------------
    comment: Implementacao de um timer para medir o tempo decorrido entre o inicio e o fim de uma operacao, como a execucao de uma consulta SQL.
    ==========================================================================================------------------------------------
*/

class TTimer {
    constructor(onStart, onStop, onTimer) {
        this.dt_inicio = null;
        this.dt_fim    = null;
        this.onStart   = onStart;
        this.onStop    = onStop;
        this.onTimer   = onTimer;
    }

    start() {
        this.dt_inicio = new Date();
        this.dt_fim    = null;
        this.run();
        this.onStart();  
    }
    
    run() {
        const d1 = this.dt_inicio;
        const d2 = this.dt_fim == null ? new Date() : this.dt_fim;
        let diffMs = Math.abs(d2 - d1);

        const horas = Math.floor(diffMs / (1000 * 60 * 60));
        diffMs %= (1000 * 60 * 60);

        const minutos = Math.floor(diffMs / (1000 * 60));
        diffMs %= (1000 * 60);

        const segundos = Math.floor(diffMs / 1000);
        const milissegundos = diffMs % 1000;

        const pad = (n, size = 2) => String(n).padStart(size, '0');

        this.onTimer( `${pad(horas)}:${pad(minutos)}:${pad(segundos)}` + (this.dt_fim == null ? "" : `:${pad(milissegundos, 3)}`) );

        if ( this.dt_fim == null ) {
            setTimeout(() => {
                this.run();
            }, 1000);
        }        
    }

    stop() {
        this.dt_fim = new Date();
        this.onStop(); 
    }
}