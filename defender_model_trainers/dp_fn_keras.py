#!/usr/bin/env python
# coding: utf-8
import pickle
import os

import numpy as np
import tensorflow as tf
import random as python_random
from tensorflow_privacy.privacy.optimizers.dp_optimizer_keras import DPKerasAdamOptimizer

np.random.seed(20)
python_random.seed(123)
tf.random.set_seed(3)


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pickle_file = os.path.join(parent_dir,'data/QMNIST_tabular_ppml.pickle')

NUM_CLASSES = 10
with open(pickle_file, 'rb') as f:
    pickle_data = pickle.load(f)
    x_defender = pickle_data['x_defender']
    y_defender = pickle_data['y_defender']
    del pickle_data
y_defender = tf.keras.utils.to_categorical(y_defender[:,0],num_classes=10)
print('Data loaded.')

def defender_model_fn_dp():
    """The architecture of the defender (victim) model.
    The attack is white-box, hence the attacker is assumed to know this architecture too."""

    model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation=tf.nn.relu),
    tf.keras.layers.Dense(NUM_CLASSES, activation=tf.nn.softmax)
    ])
        
    train_op = DPKerasAdamOptimizer(l2_norm_clip=1.0,
        noise_multiplier=1.1,
        num_microbatches=1,
        learning_rate=1e-4
       )
    
    model.compile(optimizer=train_op,
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

model = defender_model_fn_dp()

with tf.device("cpu:0"):
    model.fit(x_defender, y_defender, epochs=100, batch_size=64, validation_split=0.5, shuffle=False)

model.save(os.path.join(parent_dir,'defender_trained_models','dp_fn'))