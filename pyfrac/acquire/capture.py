import telnetlib
import ftplib
import time
import re
from pyfrac.utils.misc import ignored
from pyfrac.utils import pyfraclogger
import atexit
import os

class ICDA320:
    """
    Class of Telnet commands for FLIR A320 Camera
    """
    def __init__(self, host, port=23):
        """
        Parameters:
        -----------
        HOST: str
            host ip address of A320.
        PORT: int
            port number of the telnet service on the A320

        """
        with ignored(OSError):
            os.mkdir('./ir_images')
        self.basedir = './ir_images/'
        self.eof = "\r\n"
        self.prompt = "\>"
        self.tn = telnetlib.Telnet()
        self.ftp = ftplib.FTP(host)
        self.tn.open(host, port)
        self.tn.read_until(self.prompt)
        self.ftp.login("flir", "3vlig")
        self.logger = pyfraclogger.pyfraclogger(loggername=__name__,
                                                tofile=False)
        atexit.register(self.cleanup)
        
    # Parse the output
    def read(self, output):
        return filter(lambda x: x not in ["", self.eof],
                      output)

    # Get cam version
    def version(self):
        self.tn.write("version"+self.eof)
        self.read(self.tn.read_until(self.prompt))
    
    # Capture the image
    def capture(self):
        self.tn.write("palette"+self.eof)
        self.read(self.tn.read_until(self.prompt))
        fname = str(time.time())
        self.logger.info("Capturing "+fname)
        self.tn.write("store -j %s.jpg"%fname+self.eof)
        self.read(self.tn.read_until(self.prompt))

    # Grab the file back to this device
    def fetch(self, filename=None, pattern=None):
        """
        Download the file(s) from the Camera
        Parameters:
        -----------
        filename: str
            Name of the file to be fetched.
        pattern: str
            Regex expression for the files to
            be fetched. 
            Note: If `pattern` is passed, `filename`
            will be ignored. Expression is case sensitive
        
        Returns:
        --------
        True: bool
            If the fetching was successful.
        Exception: str
            If the fetching was unsuccessful.
        """
        def _getFile(fname):
            with ignored(Exception):
                self.logger.info("Fetching "+str(fname))
                self.ftp.retrbinary('RETR '+fname, open(
                    os.path.join(self.basedir,fname), 'wb').write)
                
        def _removeFile(fname):
            if os.path.isfile(os.path.join(self.basedir,fname)):
                with ignored(Exception):
                    self.logger.info("Removing "+str(fname))
                    self.ftp.delete(fname)
                
        dirlisting = []
        dirs = []
        self.ftp.cwd('/')
        self.ftp.dir(dirlisting.append)
        
        for i in dirlisting:
            dirs.append(i.split(" ")[-1])
            
        if pattern:
            files = [x for x in dirs if re.search(pattern, x)]
        else:
            files = [x for x in dirs if filename in x]
            
        #Download the Files
        for fname in files:
            _getFile(fname)
            time.sleep(1)
            _removeFile(fname)

            
    def cleanup(self):
        self.ftp.quit()
        self.tn.close()
