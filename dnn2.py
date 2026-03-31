import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import Input, Dense
from keras.optimizers import Adam
import joblib
import matplotlib.pyplot as plt
import pathlib
from util import GetDfAllSynt
from tensorflow.keras.regularizers import l2
from keras.callbacks import  EarlyStopping, ReduceLROnPlateau


noiseAmount =0.0


def get_current_file_path():     
    file_path = str(pathlib.Path(__file__).parent.resolve())  +'\\'   
    return file_path

dfAll=GetDfAllSynt(noiseAmount)

dfAll=dfAll[dfAll.Y!=2] #poistetaan vahvuudet 25 ja 50
dfAll=dfAll[dfAll.Y!=3]

#dfAll.to_csv(get_current_file_path()+"dfAll.csv", index=False)

X=dfAll.drop('Y', axis=1)

Y=dfAll['Y']

Y.replace(1,12.5, inplace=True)
Y.replace(4,100,inplace=True)


## Splitataan data
trainX, testX, trainY, testY = train_test_split(X, Y, test_size=0.2, stratify=Y)


## Skaalaus
scaler = StandardScaler()
trainX = scaler.fit_transform(trainX)
testX=scaler.transform(testX)
joblib.dump(scaler, get_current_file_path()+'scaler.pkl')


"""scalerY = StandardScaler()
trainY = scaler.fit_transform(pd.DataFrame(trainY))
testY=scaler.transform(pd.DataFrame(testY))
joblib.dump(scalerY, get_current_file_path()+'scalerY.pkl')"""




## Mallin rakennus
model = Sequential([
    Input(shape=(X.shape[1],)),
    Dense(8, activation='relu',kernel_regularizer=l2(0.001)),
    Dense(4, activation='relu',kernel_regularizer=l2(0.001)),
    Dense(1)
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='mse',
    metrics=['mae']
)

early_stop = EarlyStopping(monitor='val_loss', mode='min', patience=5,restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_mae', mode='min', factor=0.5, patience=3, min_lr=1e-5)

## Mallin kouluttaminen
history=model.fit(
    trainX, trainY,
    validation_data=(testX, testY),  
    epochs=50,
    batch_size=32,
    verbose=1,
    callbacks=[early_stop, reduce_lr]

)

model.save(get_current_file_path()+'malli2.keras')

## Mallin evaluaatio
loss, mae=model.evaluate(testX, testY)

plt.plot(history.history['mae'], 'b', label="train")
plt.plot(history.history['val_mae'], 'r', label="val")
plt.legend()
plt.show()

print(f"Loss: {loss}")
print(f"MAE: {mae}")
