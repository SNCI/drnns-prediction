## Loads best checkpointed model and makes prediciton on test set

from __future__ import print_function
import sys
import math
import numpy as np
from itertools import product
import cPickle as pkl

from keras import backend as K
from keras.utils.vis_utils import plot_model, model_to_dot
from keras.models import Sequential
from keras.layers import GRU, Dense, Masking, Dropout, Activation
from keras.callbacks import Callback, EarlyStopping, ModelCheckpoint
from keras.optimizers import RMSprop

from utils import set_trace, plot_ROC

# Load saved data

print('Load saved test data')

X_train = pkl.load(open('data/X_train_patents.np', 'rb'))
X_val = pkl.load(open('data/X_val_patents.np', 'rb'))
X_test = pkl.load(open('data/X_test_patents.np', 'rb'))

y_train = pkl.load(open('data/y_train_sales.np', 'rb')) # sales
y_val = pkl.load(open('data/y_val_sales.np', 'rb')) # sales

# Define network structure

nb_timesteps = 1 
nb_classes = 2
nb_features = X_test.shape[1]
output_dim = 1

# Define cross-validated model parameters

batch_size = 8
dropout = 0.5
activation = 'sigmoid'
nb_hidden = 128
initialization = 'glorot_normal'

# # Reshape X to three dimensions
# # Should have shape (batch_size, nb_timesteps, nb_features)

X_train = np.resize(X_train, (X_train.shape[0], nb_timesteps, X_train.shape[1]))
X_train = X_train[2:X_train.shape[0]] # drop first 2 samples so batch size is divisible 

X_val= np.resize(X_val, (X_val.shape[0], nb_timesteps, X_val.shape[1]))
X_val = X_val[1:X_val.shape[0]] # drop first sample so batch size is divisible 

X_test= np.resize(X_test, (X_test.shape[0], nb_timesteps, X_test.shape[1]))

# Reshape y to two dimensions
# Should have shape (batch_size, output_dim)

y_train = np.resize(y_train, (y_train.shape[0], output_dim))
y_train = y_train[2:y_train.shape[0]] # drop first 2 samples so batch size is divisible 

y_val = np.resize(y_val, (y_val.shape[0], output_dim))
y_val = y_val[1:y_val.shape[0]] # drop first sample so batch size is divisible 

y_test = np.resize(y_test, (y_test.shape[0], output_dim))

# Initiate sequential model

print('Initializing model')

model = Sequential()

# Stack layers
# expected input batch shape: (batch_size, nb_timesteps, nb_features)
# note that we have to provide the full batch_input_shape since the network is stateful.
# the sample of index i in batch k is the follow-up for the sample i in batch k-1.
model.add(Masking(mask_value=0., batch_input_shape=(batch_size, nb_timesteps, nb_features))) # embedding for variable input lengths
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization,
               batch_input_shape=(batch_size, nb_timesteps, nb_features)))
model.add(Dropout(dropout))  
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout))
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout)) 
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout)) 
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout)) 
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout))
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout))
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout))
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout))
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout))
model.add(GRU(nb_hidden, return_sequences=True, stateful=True, init=initialization))  
model.add(Dropout(dropout))
model.add(GRU(nb_hidden, stateful=True, init=initialization))  
model.add(Dropout(dropout)) 
model.add(Dense(output_dim, activation=activation))

# Visualize model

plot_model(model, to_file='results/final_model.png', # Plot graph of model
  show_shapes = True,
  show_layer_names = False)

model_to_dot(model,show_shapes=True,show_layer_names = False).write('results/final_model.dot', format='raw', prog='dot') # write to dot file

# Load weights
model.load_weights(sys.argv[-1])

# Configure learning process

model.compile(optimizer='rmsprop',
              loss='mean_absolute_error',
              metrics=['mean_absolute_error'])

print("Created model and loaded weights from file")

# Evaluation 

print('Generate predictions on test data')

y_pred_test = model.predict(X_test, batch_size=batch_size, verbose=1) # generate output predictions for test samples, batch-by-batch

np.savetxt("results/ok-pred/sales-test-pred.csv", y_pred_test, delimiter=",")

# Get fits on training and validation set for plots

print('Generate predictions on training set')

y_pred_train = model.predict(X_train, batch_size=batch_size, verbose=1) 

np.savetxt("results/ok-pred/sales-train-pred.csv", y_pred_train, delimiter=",")

print('Generate predictions on validation set')

y_pred_val = model.predict(X_val, batch_size=batch_size, verbose=1) 

np.savetxt("results/ok-pred/sales-val-pred.csv", y_pred_val, delimiter=",")