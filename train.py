#imports
from pdf2jpg import pdf2img

class Train(object):
    """
    Training simulation
    """
    def __init__(self, model, train_dir, val_dir=None):
        self.train_dir = train_dir
        self.model = model

    def process_pdf(self):
        """
        Creates images per pdf inside the class directory (multiprocessing)
        Requirement:
            PDFs should be put in their respective class directories
        """
        pdf2img(self.train_dir)
    def action(self):
        """
        Starts training the model
        """
        self.process_pdf()
        self.model.train()
        