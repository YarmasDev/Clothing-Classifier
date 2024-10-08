import tensorflow as tf
import tensorflow_datasets as tfds
import matplotlib.pyplot as plt
import numpy as np
import math

#Descargar set de datos de Fashion MNIST de Zalando
datos, metadatos = tfds.load('fashion_mnist', as_supervised=True, with_info=True)

#Imprimir los metadatos para ver que trae el set
metadatos

#Obtenemos en variables separadas los datos de entrenamiento (60k) y pruebas (10k)
datos_entrenamiento, datos_pruebas = datos['train'], datos['test']

#Etiquetas de las 10 categorias posibles
nombres_clases = metadatos.features['label'].names

nombres_clases

import cv2
datos_entrenamiento = []
for i, (imagen, etiqueta) in enumerate(datos['train']): #Todos los datos
  imagen = cv2.resize(imagen.numpy(), (28, 28))
  imagen = imagen.reshape(28, 28, 1)
  datos_entrenamiento.append([imagen, etiqueta])

datos_pruebas = []
for i, (imagen, etiqueta) in enumerate(datos['test']): #Todos los datos
  imagen = cv2.resize(imagen.numpy(), (28, 28))
  imagen = imagen.reshape(28, 28, 1)
  datos_pruebas.append([imagen, etiqueta])

x_entrenamiento = [] #imagenes de entrada (pixeles)
y_entrenamiento = [] #etiquetas
for imagen, etiqueta in datos_entrenamiento:
  x_entrenamiento.append(imagen)
  y_entrenamiento.append(etiqueta)

x_validacion = [] #imagenes de entrada (pixeles)
y_validacion = [] #etiquetas
for imagen, etiqueta in datos_pruebas:
  x_validacion.append(imagen)
  y_validacion.append(etiqueta)

x_entrenamiento, x_validacion = np.array(x_entrenamiento).astype(float) / 255 , np.array(x_validacion).astype(float) / 255
y_entrenamiento, y_validacion = np.array(y_entrenamiento), np.array(y_validacion)

plt.figure(figsize=(20, 8))
for i in range(10):
  plt.subplot(2, 5, i+1)
  plt.xticks([])
  plt.yticks([])
  plt.imshow(x_entrenamiento[i].reshape(28, 28), cmap="gray")

#Realizar el aumento de datos con varias transformaciones. Al final, graficar 10 como ejemplo
from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(
      rotation_range=20,
      width_shift_range=0.1,
      height_shift_range=0.1,
      shear_range=10,
      zoom_range=[0.75, 1.35],
      horizontal_flip=True,
  )

datagen.fit(x_entrenamiento)

plt.figure(figsize=(20,4))

for imagen, etiqueta in datagen.flow(x_entrenamiento, y_entrenamiento, batch_size=20, shuffle=True):
  for i in range(20):
    plt.subplot(2, 10, i+1)
    plt.xticks([])
    plt.yticks([])
    plt.imshow(imagen[i].reshape(28, 28), cmap="gray")
  break

modeloCNN_AD = tf.keras.models.Sequential([
    tf.keras.layers.Input(shape=(28, 28, 1)),
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),

    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(10, activation='softmax')
])

learning_rate = 0.001
modeloCNN_AD.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

#Usamos la funcion flow del generador para crear un iterador que podamos enviar como entrenamiento a la funcion FIT del modelo
data_gen_entrenamiento = datagen.flow(x_entrenamiento, y_entrenamiento,  shuffle=True)

datagen_validacion = ImageDataGenerator()
data_gen_validacion = datagen_validacion.flow(x_validacion, y_validacion,shuffle=False)

# Usamos tf.data.Dataset para la validación
dataset_validacion = tf.data.Dataset.from_tensor_slices((x_validacion, y_validacion))
dataset_validacion = dataset_validacion.batch(64)

historial = modeloCNN_AD.fit(
    data_gen_entrenamiento,
    epochs=10,
    validation_data= dataset_validacion
)

#Ver la funcion de perdida
plt.xlabel("# Epoca")
plt.ylabel("Magnitud de pérdida")
plt.plot(historial.history["loss"])

# Seleccionar un lote de imágenes del conjunto de validación
imagenes_prueba = x_validacion[120:145]  # Cambia el número según cuántas imágenes quieras probar

# Hacer las predicciones
predicciones = modeloCNN_AD.predict(imagenes_prueba)

# Mostrar las predicciones junto con las imágenes
for i in range(len(imagenes_prueba)):
    plt.figure()
    plt.imshow(imagenes_prueba[i].reshape(28, 28), cmap="gray")
    plt.title("Predicción: " + nombres_clases[np.argmax(predicciones[i])])
    plt.show()

# Seleccionar una imagen del conjunto de validación
imagen_prueba = x_validacion[1222]  # Cambia el índice según la imagen que quieras probar

# Expande las dimensiones para que coincidan con el formato que espera el modelo (1, 28, 28, 1)
imagen_prueba = np.expand_dims(imagen_prueba, axis=0)

# Hacer la predicción
prediccion = modeloCNN_AD.predict(imagen_prueba)

# Mostrar la predicción
print("Predicción: ", nombres_clases[np.argmax(prediccion[0])])

# Mostrar la imagen
plt.imshow(imagen_prueba[0].reshape(28, 28), cmap="gray")
plt.title("Predicción: " + nombres_clases[np.argmax(prediccion[0])])
plt.show()

#PREDECIMOS CON UNA IMAGEN EXTERNA

from tensorflow.keras.preprocessing import image
from PIL import Image, ImageOps, ImageEnhance


# Cargar y convertir la imagen a escala de grises
image_path = "pantalon.jpg"
image = Image.open(image_path).convert("L")  # Convertir a escala de grises

# Opcional: Ajustar el contraste
enhancer = ImageEnhance.Contrast(image)
image = enhancer.enhance(-10.0)  # Puedes ajustar este valor para incrementar el contraste

# Redimensionar la imagen a 28x28 píxeles
image = image.resize((28, 28))

# Convertir la imagen a un array de numpy y normalizar
image_array = np.asarray(image)
image_array = image_array / 255.0

# Asegurarse de que tiene la forma correcta (28, 28, 1)
image_array = np.expand_dims(image_array, axis=-1)

# Preparar la imagen para la predicción (añadir dimensión para el batch)
image_array = np.expand_dims(image_array, axis=0)

# Visualizar la imagen procesada (escala de grises)
plt.imshow(image_array[0, :, :, 0], cmap='gray')
plt.show()

# Hacer la predicción
prediccion = modeloCNN_AD.predict(image_array)
print("Predicción: " + nombres_clases[np.argmax(prediccion[0])])
