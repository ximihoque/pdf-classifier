#imports 
from prediction import Prediction
from train import Train
from model import Model

class Simulation(object):
    """
    Performs pipeline simulation 
    """
    def __init__(self, mode):
        self.mode_ = mode
    
    def simulate(self):
        self.mode_.action()

if __name__ == '__main__':
    sim = Simulation(Prediction("test", Model(model_dir="model_dir")))
    sim.simulate()

    



    