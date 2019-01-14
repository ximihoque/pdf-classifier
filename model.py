#imports
import tensorflow as tf
import time, os, glob
from utils import load_image
from keras.preprocessing.image import ImageDataGenerator
import config

class Model(object):
    """
    Wrapper for keras model for image classification 
    """
    def __init__(self, model_dir, train_dir=None, train=False, valid_dir=None):
        """
        Args:
            model_dir: (str), Directory to export saved model, or load saved model. 
            train_dir: (str), Directory for images to be trained
            train: (bool), for training mode or prediction mode
            valid_dir: (str), Directory for validation data.
        """
        self.train_dir = train_dir
        self.model_dir = model_dir
        self.valid_dir = valid_dir

        #In prediction mode
        if not train:
            self.model = self.load_model()
            self.model.load_weights(self.latest_weights())
            self.classes = config.classes

    def load_model(self):
        classifier = tf.keras.models.Sequential()
        classifier.add(tf.keras.layers.Conv2D(32, (3, 3), input_shape=(64, 64, 3),
                        activation='relu'))
        classifier.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))
        classifier.add(tf.keras.layers.Conv2D(32, (3, 3), activation='relu'))
        classifier.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))
        classifier.add(tf.keras.layers.Flatten())
        classifier.add(tf.keras.layers.Dense(units=128, activation='relu'))
        classifier.add(tf.keras.layers.Dense(units=4, activation='softmax'))  
        return classifier

    def data_generator(self):
        train_imagedata = ImageDataGenerator(rescale=1. / 255, shear_range=0.2,
          zoom_range=0.2, horizontal_flip=True)
        test_imagedata = ImageDataGenerator(rescale=1. / 255)
        training_set = \
            train_imagedata.flow_from_directory(self.train_dir
                , target_size=(64, 64), batch_size=32, class_mode='categorical')
        
        #TODO:
        #handle if validation data not present
        test_set = \
            test_imagedata.flow_from_directory('Samples_old'
                , target_size=(64, 64), batch_size=32, class_mode='categorical')
        #Update the config when this method is invoked
        #reverse the mapping
        config.classes = {j:i for i,j in zip(training_set.class_indices.keys(), 
                                training_set.class_indices.values()) }
        return training_set, test_set 


    def train(self):
        """
        Starts training model and returns history logs
        """
        model=self.load_model()
        training_set, test_set=self.data_generator()
        tpu_model = tf.contrib.tpu.keras_to_tpu_model(
            model,
            strategy=tf.contrib.tpu.TPUDistributionStrategy(
                tf.contrib.cluster_resolver.TPUClusterResolver(tpu='grpc://' + os.environ['COLAB_TPU_ADDR'])
            )
        )
        tpu_model.compile(tf.train.AdamOptimizer(), loss='categorical_crossentropy',
                            metrics=['accuracy'])
        history=tpu_model.fit_generator(training_set, steps_per_epoch=10, epochs=20,
                                    validation_data=test_set,
                                    validation_steps=5)
        self.model = tpu_model
        self.export_model(tpu_model)
        return history

    def export_model(self, model):
        """
        Exports model weights with current timestamp in (.h5) format 
        """
        t = time.localtime()
        timestamp = time.strftime('%b-%d_%H%M', t)
        model.save_weights(timestamp+'.h5')

    def latest_weights(self):  
        """
        Gets latest weight file from directory
        Weight file type: .h5
        """
        list_of_files = glob.glob(os.path.join(self.model_dir, "*.h5")) # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
   
    def predict(self, img_path):
        """
        Predicts class label for image
        """
        img_tensor = load_image(img_path)
        return self.classes[self.model.predict_classes(img_tensor)[0]]
        
        #idx = argmax(model.predict)
        #check if a[idx] > threshold
        # true --> self.classes[self.model.predict_classes(img_tensor)[0]]
        #false --> others
        #return self.model.predict(img_tensor)
