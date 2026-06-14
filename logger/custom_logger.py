import logging
import os
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self,log_dir='logs'):

        # Ensure the directory exists
        self.log_dir = os.path.join(os.getcwd(),log_dir)
        os.makedirs(self.log_dir,exist_ok=True)
        
        # create time stamped log file name
        log_file = f"{datetime.now().strftime('%m_%d_%y_%H_%M_%S')}.log"

        self.log_file_path = os.path.join(self.log_dir,log_file)

        ## Configure logging
        #logging.basicConfig(
            #filename = log_file_path,
           # format = "[%(asctime)s] %(levelname)s %(name)s (line:%(lineno)d) - %(message)s",
            #level = logging.INFO,
       # )

    def get_logger(self,name =__file__):
        logger_name = os.path.basename(name)
        
        # Configure logging for console + file (both json)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
         
        logging.basicConfig(
            level = logging.INFO,
            format = "%(message)s",
            handlers=[file_handler,console_handler],
        ) 

       # configure the struct log for json structured logging 
        structlog.configure(
           processors=[
        # Adds a timestamp to every log entry
         structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
        # Adds the log level like info or error
         structlog.processors.add_log_level,
        # Changes the default 'event' key name if needed
         structlog.processors.EventRenamer(to="event"),
        # Turns the log data into a JSON string
         structlog.processors.JSONRenderer(),
           ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,

         )
        return structlog.get_logger(logger_name)


if __name__ == "__main__":
    logger = CustomLogger().get_logger(__file__)
    logger.info("Test",user_id=123,file_name = "report.pdf")
    logger.error("Failed to process PDF", error="File not found", user_id=123)