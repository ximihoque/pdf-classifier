#imports
from pdf2jpg import export
from multiprocessing import Pool, Process, Queue
import glob, os, time
from itertools import product
from shutil import copyfile
import multiprocessing
import logging, monitor
logging.basicConfig(level=logging.DEBUG)

#from functools import partial
#from contextlib import contextmanager

"""@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()
"""

class Prediction(object):
    """
    Prediction Simulation
    """
    def __init__(self, source, model):
        #Model initialization
        self.model = model

        #Multi-processing vars
        self.queue = Queue()         #for prediction process
        self.pdf_monitor = Queue()   #for pdf processing process

        #Pdf directory (hard coded)
        self.dir_ = source           #Pdf
        self.output_dir = "output"   #Result

    def process_pdf(self, single=False):
        """
        Creates images per pdf inside the class directory (multiprocessing)
        """
    
        pdf_files = glob.glob(os.path.join(self.dir_, "*.pdf"))

        #with poolcontext(processes=3) as pool:
        #   pool.map(partial(export, in_dir=True, q=self.queue), pdf_files)
        map(lambda pdf_file: export(pdf_file, True, self.queue), pdf_files)

        while True:
            pdf_file = self.pdf_monitor.get()
            logging.debug("New pdf Detected: {}".format(pdf_file))
            export(pdf_file, True, self.queue)

    def predict_pdf(self, pdf_path):
        """
        Combines predictions of multiple images for same pdf
        Returns: str, class label for pdf
        """
        
        pdf_dir = pdf_path.strip(".pdf")
        
        predictions = [self.model.predict(os.path.join(pdf_dir, img_name))  for img_name in os.listdir(pdf_dir)]
        items = {predictions.count(i):i for i,_ in predictions}
        return items[max(items.keys())]

    def shelf_pdf(self, pdf_path, shelf):
        """
        Puts the pdf into the shelf directory
        """
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        if not os.path.exists(shelf):
            os.mkdir(shelf)    
        copyfile(pdf_path, os.path.join(shelf,pdf_path.split('/')[-1]))

    def action(self):
        """
        Performs prediction simulation actions
        """
        #Starting PDF --> JPG process 
        p1 = Process(target=self.process_pdf)
        p1.start()
        logging.info("PDF --> JPG started")
        
        #Monitoring for pdfs in directory and processing them
        monitor.queue = self.pdf_monitor
        w = monitor.Watcher()
        w.run()

        while True:
            processed_pdf = self.queue.get()
            logging.info("Fetched: {}".format(processed_pdf)) 
            shelf = self.predict_pdf(processed_pdf)
            logging.info("Shelving...")
            self.shelf_pdf(processed_pdf, shelf=os.path.join(self.output_dir, shelf))
