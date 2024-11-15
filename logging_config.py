import logging

def configure_logging():
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s", 
        handlers=[
            logging.FileHandler("app.log"),  
            logging.StreamHandler()       
        ]
    )
    logging.info("Logging system is configured")