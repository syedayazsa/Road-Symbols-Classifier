# -*- coding: utf-8 -*-
"""roadsymbolclassifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hCHczoa3BSaH-w5SYN--3ieWKb3ipoWx
"""

!git clone https://bitbucket.org/jadslim/german-traffic-signs/

!ls german-traffic-signs

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.utils.np_utils import to_categorical
from tensorflow.python.keras.layers import Dropout, Flatten
from tensorflow.python.keras.layers.convolutional import Conv2D, MaxPooling2D
import pickle
np.random.seed(0)

with open('german-traffic-signs/train.p', 'rb') as f: #storing in variable f
  train_data = pickle.load(f)
with open('german-traffic-signs/valid.p', 'rb') as f:
  val_data = pickle.load(f)
with open('german-traffic-signs/test.p', 'rb') as f:
  test_data = pickle.load(f)

print(type(test_data))

X_train, y_train = train_data['features'], train_data['labels']
X_val, y_val = val_data['features'], val_data['labels']
X_test, y_test = test_data['features'], test_data['labels']

print(X_train.shape)
print(X_val.shape)
print(X_test.shape)

assert(X_train.shape[0] == y_train.shape[0]), "The number of images not equal to number of labels" 
assert(X_val.shape[0] == y_val.shape[0]), "The number of images not equal to number of labels" 
assert(X_test.shape[0] == y_test.shape[0]), "The number of images not equal to number of labels"
assert(X_train.shape[1:] == (32,32,3)), "The dimensions of the images are ot 32*32*3"
assert(X_val.shape[1:] == (32,32,3)), "The dimensions of the images are ot 32*32*3"
assert(X_test.shape[1:] == (32,32,3)), "The dimensions of the images are ot 32*32*3"

import pandas as pd
data = pd.read_csv('german-traffic-signs/signnames.csv')
print(data)

#Plotting image belonging to every class
import random
num_of_samples=[]
cols = 5
num_classes = 43
  
fig, axs = plt.subplots(nrows=num_classes, ncols=cols, figsize=(5,50))
fig.tight_layout()
  
for i in range(cols):
    for j, row in data.iterrows():
      x_selected = X_train[y_train == j]
      axs[j][i].imshow(x_selected[random.randint(0,(len(x_selected) - 1)), :, :], cmap=plt.get_cmap('gray'))
      axs[j][i].axis("off")
      if i == 2:
        axs[j][i].set_title(str(j) + " - " + row["SignName"])
        num_of_samples.append(len(x_selected))

# Training data distribution
print(num_of_samples)
plt.figure(figsize = (12, 4))
plt.bar(range(0, num_classes), num_of_samples)
plt.title("Distribution of the training dataset")
plt.xlabel("Class Number")
plt.ylabel("Number of Images")
plt.show()



"""---


# ***The bar-graph shows that the variation in number of images range from 180 to 2010 thus, we have to preprocess the data accordingly.***

---
"""

import cv2

plt.imshow(X_train[1000])
plt.axis("off")
print(X_train[1000].shape)
print(y_train[1000])

def grayscale(img):
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  return img

img = grayscale(X_train[1000])
plt.imshow(img)
plt.axis("off")

"""# **USING HISTOGRAM EQUALIZATION TO EVEN UP THE LIGHTING IN TRAINING DATA.**"""

def equalize(img):
  cv2.equalizeHist(img)
  return img

img = equalize(img)
plt.imshow(img)
plt.axis('off')

def preprocessing(img):
  img = grayscale(img)
  img = equalize(img)
  img = img/255 #normalizing
  return img

X_train = np.array(list(map(preprocessing, X_train))) #Preprocessing
X_val = np.array(list(map(preprocessing, X_val)))
X_test = np.array(list(map(preprocessing, X_test)))

plt.imshow(X_train[random.randint(0, len(X_train)-1)])
plt.axis('off')
print(X_train.shape)

"""# **ADDING DEPTH TO THE DATA BY RESHAPING IT**"""

X_train = X_train.reshape(34799, 32, 32, 1)
X_test = X_test.reshape(12630, 32, 32, 1)
X_val = X_val.reshape(4410, 32, 32, 1)

#Data Augmentation
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
datagen = ImageDataGenerator(width_shift_range = 0.1,
                   height_shift_range = 0.1,
                   zoom_range = 0.2, # zoom from 0.8 to 1.2
                   shear_range = 0.1,
                   rotation_range = 10)
datagen.fit(X_train)

#Create new images
batches = datagen.flow(X_train, y_train, batch_size = 15)
X_batch, y_batch = next(batches)
 
fig, axs = plt.subplots(1, 15, figsize=(20, 5))
fig.tight_layout()
 
for i in range(15):
    axs[i].imshow(X_batch[i].reshape(32, 32))
    axs[i].axis("off")
 
print(X_batch.shape)

print(X_train.shape)
print(X_test.shape)
print(X_val.shape)

#One hot encoding labels
y_train = to_categorical(y_train, 43)
y_val = to_categorical(y_val, 43)
y_test = to_categorical(y_test, 43)

def LeNet_model():
    model = Sequential()
    model.add(Conv2D(30, (5, 5), input_shape=(32, 32, 1), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(15, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Flatten())
    model.add(Dense(500, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))
    # Compile model
    model.compile(optimizer = 'adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

model = LeNet_model()
print(model.summary())

history = model.fit_generator(datagen.flow(X_train, y_train, batch_size = 50), steps_per_epoch = 2000, epochs = 10, 
                              validation_data = (X_val, y_val), shuffle = 1)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss')
plt.xlabel('epoch')
plt.legend(['training', 'validation'])

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.legend(['training','test'])
plt.title('Accuracy')
plt.xlabel('epoch')
plt.legend(['training', 'validation'])

score = model.evaluate(X_test, y_test, verbose=0)
print('Test score:', score[0])
print('Test accuracy:', score[1])

"""# **OBSERVATION**


*   From **Loss vs Epoch Graph**, it is observed that the validation loss > than 
*  Since the validation accuracy is trailing behind the training accuracy, it seems that the model has overfitted the train data.
*   The accuracy is low

Due to large number of classes, low training data count, it is necessary to **tune the model well.**

# **MODEL TUNING**
The following modifications are made to tune model: 


1.   Learning rate is set to 0.001
2.   Doubling the number of filters in each layer.
3. Adding a new convolution Filter
4. Adding new dropout layer
"""

def optimized_LeNet():
    model = Sequential()
    model.add(Conv2D(60, (5, 5), input_shape=(32, 32, 1), activation='relu'))
    model.add(Conv2D(60, (5, 5), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(30, (3, 3), activation='relu'))
    model.add(Conv2D(30, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    #model.add(Dropout(0.5))

    model.add(Flatten())
    model.add(Dense(500, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))
    # Compile model
    model.compile(optimizer = 'adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

model_new = optimized_LeNet()
print(model_new.summary())

history_new = model_new.fit_generator(datagen.flow(X_train, y_train, batch_size = 50), steps_per_epoch = 2000, epochs = 10, 
                              validation_data = (X_val, y_val), shuffle = 1)

plt.plot(history_new.history['loss'])
plt.plot(history_new.history['val_loss'])
plt.title('Loss')
plt.xlabel('epoch')
plt.legend(['training', 'validation'])

plt.plot(history_new.history['accuracy'])
plt.plot(history_new.history['val_accuracy'])
plt.legend(['training','test'])
plt.title('Accuracy')
plt.xlabel('epoch')
plt.legend(['training', 'validation'])

score_new = model_new.evaluate(X_test, y_test, verbose=0)
print('Test score:', score[0])
print('Test accuracy:', score[1])

"""# **TESTING**"""

import requests
from PIL import Image
url = 'https://previews.123rf.com/images/pejo/pejo0907/pejo090700003/5155701-german-traffic-sign-no-205-give-way.jpg'
r = requests.get(url, stream=True)
img = Image.open(r.raw)
plt.imshow(img, cmap=plt.get_cmap('gray'))

#Preprocessing the image
img = np.asarray(img)
img = cv2.resize(img, (32, 32))
img = preprocessing(img)
plt.imshow(img, cmap = plt.get_cmap('gray'))
print(img.shape)

#Reshape
img = img.reshape(1, 32, 32, 1)

#Test image
print("predicted sign: "+ str(model_new.predict_classes(img)))

"""# **FIT GENERATOR**
The model is not performing very good on test set, so we need to perform image augmentation.

# **SAVING THE MODEL**
"""

model.save('model.h5')
from google.colab import files
files.download('model.h5')