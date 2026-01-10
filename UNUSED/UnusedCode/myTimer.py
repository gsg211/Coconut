from threading import Thread, Lock
import time

class myTimer():
    def __init__(self, step_in_seconds:float, notify_threshold:float, owner:str = 'None'):
        self.notify_threshold:float = notify_threshold
        self.notifications:int = 0
        
        self.stop_signal:bool = False
        
        
        self.step_in_seconds:float = step_in_seconds
        self.lock:Lock = Lock()  
        self.thr:Thread = Thread(target=self.worker,name='{} - TimerThread - '.format(owner,step_in_seconds))
        self.value:float = float(0)
        
    def increment(self):
        with self.lock:
            self.value = self.value + self.step_in_seconds
            if self.value >= self.notify_threshold:
                self.value = 0
                self.notifications +=1
                # print('notify')
        
        time.sleep(self.step_in_seconds)
        
        
    def get_current_value(self)->float:
        with self.lock:
            return self.value
    
    def try_consume_notification(self)->tuple[int,bool]:
        with self.lock:
            if self.notifications > 0:
                self.notifications-=1
                return (self.notifications+1,True)
            return (self.notifications,False)
        
    def notify_stop(self):
        with self.lock:
            self.stop_signal = True
        
    def worker(self):
        while self.stop_signal == False:
            self.increment()
        with self.lock:
            self.value = 0
            self.notifications = 0
            self.stop_signal = False
            
    def run(self):
        self.thr.start()
            
        