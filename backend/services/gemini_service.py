# services/gemini_service.py

import json
from dotenv import load_dotenv
from typing import List, Dict, Any


import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from backend.utils.gemini_client import GeminiClient
from backend.services.pdf_generation import generate_pdf_from_xml



class GeminiService:
    """
    Simple wrapper around GeminiClient for generating notes,
    practice questions, and written‐work analysis.
    """

    def __init__(self):
        self.client = GeminiClient() 

    def generate_notes(self, topic: str, context: str):
        xml = self.client.generate_notes(topic, context)
        print(xml)
        output = generate_pdf_from_xml(xml, output_filename="notes.pdf")
        print("Wrote PDF to", output)

    def generate_practice_questions(self, topic: str, context: str):
        xml = self.client.generate_practice_questions(topic, context)
        print(xml)
        #output = generate_pdf_from_xml(xml, output_filename="questions.pdf")
        #print("Wrote PDF to", output)


load_dotenv()
gemini = GeminiService()

gemini.generate_practice_questions("Artificial Neural Networks", """Artificial neural networks (ANNs) are computational models inspired by the layered structure of the human brain. At their core, ANNs consist of an input layer, one or more hidden layers, and an output layer. Each layer contains neurons (nodes) that compute a weighted sum of their inputs, apply a nonlinear activation function (e.g., ReLU, sigmoid, tanh), and pass the result to the next layer. During training, the network minimizes a loss function—such as mean squared error for regression or cross‑entropy for classification—by adjusting weights via backpropagation and an optimization algorithm (e.g., stochastic gradient descent, Adam, RMSProp).


Key architecture variants include:
- **Feedforward Networks**: Data flows in one direction from input to output; simplest form of ANN.  
- **Convolutional Neural Networks (CNNs)**: Use convolutional layers to process spatial data like images, leveraging local connectivity and weight sharing.  
- **Recurrent Neural Networks (RNNs)**: Maintain internal state (memory) across sequences; useful for time‑series or language data.  
- **Transformers**: Employ self‑attention mechanisms to model long‑range dependencies without recurrence.


Common training challenges and mitigation strategies:
- **Overfitting**: When a model captures noise in the training set and fails to generalize.  
  - *Regularization*: L1/L2 weight penalties to constrain complexity.  
  - *Dropout*: Randomly deactivate neurons during training to build robustness.  
  - *Early Stopping*: Halt training when validation performance plateaus.  
- **Vanishing/Exploding Gradients**: Gradients become too small or large in deep networks.  
  - *Weight Initialization*: Methods like Xavier/He initialization.  
  - *Gradient Clipping*: Cap gradient values to a fixed range.  
- **Hyperparameter Tuning**: Learning rate, batch size, number of layers/neurons—often performed via grid search, random search, or Bayesian optimization.


Typical use cases span computer vision (image classification, object detection), natural language processing (machine translation, sentiment analysis), and reinforcement learning (game playing, robotics). Hardware acceleration using GPUs and distributed training across multiple machines has become essential for scaling up deep learning workloads.
""")