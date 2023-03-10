# -*- coding: utf-8 -*-
"""Proyek Akhir Dicoding.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1a15JPKDyDHcy6kgmJ-b-tFsUC_G1ygIP
"""

#mengkoneksikan google drive

from google.colab import drive
drive.mount("/content/gdrive/", force_remount=True)

# Commented out IPython magic to ensure Python compatibility.
#memilih path

# %cd /content/gdrive/My Drive/Dicoding Machine Learning/

#konfigurasi kaggle 

import os
os.environ['KAGGLE_CONFIG_DIR'] = "/content/gdrive/My Drive/Dicoding Machine Learning/"

!kaggle datasets download -d hasibalmuzdadid/shoe-vs-sandal-vs-boot-dataset-15k-images

#unzipping the zip files and deleting the zip files
!unzip \*.zip  && rm *.zip

#Import library

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import keras
import os
import pathlib
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras import layers
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense, Input
from keras.callbacks import EarlyStopping
from keras.utils import load_img, img_to_array
from keras.applications import MobileNetV2

Data   ='/content/gdrive/My Drive/Dicoding Machine Learning/Shoe vs Sandal vs Boot Dataset/'

#membuat class image

for image_class in os.listdir(Data) :
  print(image_class)

#membuat direktori data

img_data = tf.keras.utils.image_dataset_from_directory(Data)

datagen = ImageDataGenerator(rescale=1./255,
                             rotation_range=45,
                             horizontal_flip=True,
                             vertical_flip=True,
                             fill_mode='reflect',
                             validation_split=0.2)

train = datagen.flow_from_directory(Data,
                                    batch_size=32,
                                    target_size=(256,256),
                                    shuffle= True,
                                    class_mode="categorical",
                                    subset="training")

test = datagen.flow_from_directory(Data,
                                   batch_size=32,
                                   target_size=(256,256),
                                   class_mode="categorical",
                                   subset="validation")

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('val_accuracy')>0.93):
      print("\nPELATIHAN BERHENTI, AKURASI LEBIH DARI 93%")
      self.model.stop_training = True

callbacks = myCallback()

model=tf.keras.models.Sequential()
model.add(layers.Conv2D(16,(3,3),input_shape=[256,256,3],activation='relu'))
model.add(layers.MaxPooling2D(2,2))
model.add(layers.Conv2D(32,(3,3),activation='relu'))
model.add(layers.MaxPooling2D(2,2))
model.add(layers.Conv2D(64,(3,3),activation='relu'))
model.add(layers.MaxPooling2D(2,2))
model.add(layers.Conv2D(256,(3,3),activation='relu'))
model.add(layers.MaxPooling2D(2,2))
model.add(layers.Flatten())
model.add(layers.Dropout(0.5))
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(3, activation='softmax'))

model.summary()

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.fit(train,
          epochs=100,
          batch_size=32,
          validation_data=(test),
          callbacks=[callbacks])

#melihat plot history

import matplotlib.pyplot as mplt
acc = model.history.history['accuracy']
val_acc = model.history.history['val_accuracy']
loss = model.history.history['loss']
val_loss = model.history.history['val_loss']

epochs = range(len(acc))

mplt.plot(epochs, acc, 'r', label='Akurasi Dataset Training')
mplt.plot(epochs, val_acc, 'b', label='Akurasi Dataset Validasi')
mplt.title('akurasi dataset training dan validasi')
mplt.legend(loc=0)
mplt.figure()
mplt.show()

#melihat plot loss

mplt.plot(epochs, loss, 'r', label='Akurasi Dataset Training')
mplt.plot(epochs, val_loss, 'b', label='Akurasi Dataset Validasi')
mplt.title('loss dataset training dan validasi')
mplt.legend(loc=0)
mplt.figure()
mplt.show()

from google.colab import files

uploaded = files.upload()
 
for fn in uploaded.keys():
 
  # predicting images
  path = fn
  img = tf.keras.utils.load_img(path, target_size=(256,256,3))
  imgplot = plt.imshow(img)
  x = tf.keras.utils.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  predict=model.predict(test) 
  classes=np.argmax(predict,axis=1)
  images = np.vstack([x])
  classes = model.predict(images, batch_size=64)
  
  print(fn)
  if classes[0][0]==1:
    print('Shoe')
  elif classes[0][1]==1:
    print('Sandal')
  elif classes[0][2]==1:
    print('Boot')
  else:
    print('unknown')

# Menyimpan model dalam format SavedModel
export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)
 
# Convert SavedModel menjadi shoe.tflite
converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()
 
tflite_model_file = pathlib.Path('shoe.tflite')
tflite_model_file.write_bytes(tflite_model)