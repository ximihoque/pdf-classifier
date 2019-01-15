#imports 
from prediction import Prediction
from train import Train
from model import Model
import fire, config

class Simulation(object):
    """
    Performs pipeline simulation 
    """
    def __init__(self):
    
        self.prediction = Prediction(config.prediction_source, Model(model_dir=config.model_dir))
        self.training = Train("../Samples", "../model_dir", "../Samples_old")
    
    #def simulate(self):
     #   self.mode_.action()

if __name__ == '__main__':
    fire.Fire(Simulation)


    