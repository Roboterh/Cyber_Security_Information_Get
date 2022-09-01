import logging
class Config():
    # creating a logger对象
    logger = logging.getLogger()    

    # define the default level of the logger
    logger.setLevel(logging.INFO)  
    
    # creating a formatter
    formatter = logging.Formatter( '%(asctime)s | %(levelname)s -> %(message)s' )  
    
    # creating a handler to log on the filesystem  
    file_handler=logging.FileHandler('cve_monitor.log')
    file_handler.setFormatter(formatter)  
    file_handler.setLevel(logging.DEBUG)  
    
    # adding handlers to our logger  
    logger.addHandler(file_handler)   
    
    #logger.info('this is a log message...')  
    
    def get_config(self):    
        return self.logger