import dm
import logging
import signal
import sys

# Configure logging to write errors to a file
logging.basicConfig(
    filename='AlgarSQL.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def handle_signal(signum, frame):
    logging.critical(f"Received signal {signum}, causing core dump.")
    sys.exit(1)


signal.signal(signal.SIGSEGV, handle_signal)
signal.signal(signal.SIGABRT, handle_signal)

if __name__ == "__main__":
    try:
        dm.main()
        exit()
    except Exception as e:
        logging.error( str(e) )
        logging.error("An error occurred", exc_info=True)
