from pathlib import Path
import defines as d
import debugging.logs as logs
from datetime import datetime


class ConfigData():
    __client_id:int = 0
    __window_sz:int = 0
    __config_dir_path:Path = None
    
    def __init__(self,client_server_n:bool):
        self.path = Path(d.CLIENT_CONFIG_PATH) if client_server_n else None
        if self.path and not self.path.exists():
            raise FileNotFoundError("Client config doesn't exist")
        
        current_line_idx:int = 0
        current_line_content:str = 'none'
        with self.path.open() as f:
            while current_line_content:
                current_line_content = f.readline()
                try:
                    self.__client_id = int(current_line_content) if current_line_idx == d.Config_Line.ID_LINE else self.__client_id
                except:
                    logs.utils_logger.info("Could not transform the received client id into an int")
                try:
                    self.__window_sz = int(current_line_content) if current_line_idx == d.Config_Line.WINDOW_LINE else self.__window_sz
                except:
                    logs.utils_logger.info("Could not transform the received window sz into an int")

                current_line_idx+=1
    
    def set_and_check_config_dir(self):
        config_dir_path = Path(d.SERVER_CONFIG_DIR_PATH)
        if not config_dir_path.exists():
            raise FileExistsError("Server configurations directory doesn't exist -- this function must be called only by the server")
        
        if not config_dir_path.is_dir():
            raise FileExistsError("The specified path is not a directory -- this function must be called only by the server")
        
        self.__config_dir_path = config_dir_path
        
        
    def find_client(self,cl_id:int) -> bool:
        self.set_and_check_config_dir()
        
        for file in self.__config_dir_path.iterdir():
            current_line_content = 'None'
            with file.open() as f:
                current_line_content = f.readline()
                try:
                    if int(current_line_content) == cl_id:
                        return True
                except:
                    logs.utils_logger.info("Failed to convert line content to client ID in ConfigData, find_client()")
        return False


        
    def save_current_config(self)->bool:
        self.set_and_check_config_dir()
        current_date = str(datetime.now())
        file_path = self.__config_dir_path / current_date
        if self.__client_id == 0 or self.__window_sz == 0:
            return False
        file_path.write_text("{}\n{}".format(self.__client_id,self.__window_sz))
        return True
        
                    
                
        
    def print_data(self):
        print("cl id - {}".format(self.__client_id))
        print("window size - {}".format(self.__window_sz)) 
                
                