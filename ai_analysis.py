import tensorflow as tf
import numpy as np
import os

class MentalHealthAnalyzer:
    """
    Analyzer for mental health survey data using a TensorFlow model.
    """
    def __init__(self, model_path='model/mental_health_model.h5'):
        self.model = self._load_or_create_model(model_path)

    def _load_or_create_model(self, model_path):
        """
        Loads an existing model or creates a fresh architecture for inference.
        """
        if os.path.exists(model_path):
            return tf.keras.models.load_model(model_path)
        
        return self._build_model_architecture()

    def _build_model_architecture(self):
        """
        Defines the Keras model architecture and initializes weights.
        """
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(15,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear') 
        ])
        
        weights_layer1 = np.ones((15, 32)) * 0.1
        bias_layer1 = np.zeros(32)
        
        weights_layer2 = np.ones((32, 16)) * 0.1
        bias_layer2 = np.zeros(16)
        
        weights_out = np.ones((16, 1)) * 0.1
        bias_out = np.zeros(1)
        
        model.layers[0].set_weights([weights_layer1, bias_layer1])
        model.layers[2].set_weights([weights_layer2, bias_layer2])
        model.layers[3].set_weights([weights_out, bias_out])
        
        return model

    def analyze(self, answers):
        """
        Performs inference on the provided answers.
        
        Args:
            answers (dict): Survey answers.
            
        Returns:
            dict: Analysis result with status and recommendation.
        """
        input_data = self._preprocess(answers)
        
        prediction_tensor = self.model(input_data)
        score = float(prediction_tensor.numpy()[0][0])
        
        return self._interpret_score(score)

    def _preprocess(self, answers):
        """
        Converts answer dictionary to a tensor.
        """
        data = []
        for i in range(1, 16):
            val = answers.get(f'q{i}', 3)
            try:
                data.append(float(val))
            except ValueError:
                data.append(3.0)
        
        return tf.constant([data], dtype=tf.float32)

    def _interpret_score(self, score):
        """
        Maps the numerical model output to a clinical status.
        """
        if score < 10.0:
            status = "Low Risk"
            recommendation = "Maintain your current healthy routine."
        elif score < 20.0:
            status = "Moderate Risk"
            recommendation = "Consider mood tracking and scheduled wellness breaks."
        else:
            status = "High Risk"
            recommendation = "Immediate consultation with a counselor is recommended."
            
        return {
            'score': score,
            'status': status,
            'recommendation': recommendation
        }

def analyze_mental_health(answers):
    """
    Wrapper function for route integration.
    """
    analyzer = MentalHealthAnalyzer()
    return analyzer.analyze(answers)
