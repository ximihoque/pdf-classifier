#imports
from pdf2jpg import pdf2img
from model import Model

class Train(object):
    """
    Training simulation
    """
    def __init__(self, train_dir, model_dir, valid_dir=None):
        #self.train_dir = train_dir
        self.model = Model(model_dir, train_dir, True, valid_dir)

    def process_pdf(self):
        """
        Creates images per pdf inside the class directory (multiprocessing)
        Requirement:
            PDFs should be put in their respective class directories
        """
        pdf2img(self.model.train_dir)
    def action(self):
        """
        Starts training the model
        """
        self.process_pdf()
        self.model.train()
#Train("Samples", "model_dir")   