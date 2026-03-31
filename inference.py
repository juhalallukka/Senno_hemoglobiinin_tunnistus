import tensorflow as tf
import numpy as np
import joblib

import pathlib

def get_current_file_path():     
    file_path = str(pathlib.Path(__file__).parent.resolve())  +'\\'   
    return file_path


model1=tf.keras.models.load_model(get_current_file_path()+'malli1.keras')
model2=tf.keras.models.load_model(get_current_file_path()+'malli2.keras')
model3=tf.keras.models.load_model(get_current_file_path()+'malli3.keras')
model4=tf.keras.models.load_model(get_current_file_path()+'malli4.keras')
scaler = joblib.load(get_current_file_path()+'scaler.pkl')
scalerY = joblib.load(get_current_file_path()+'scalerY.pkl')

def GiveResult(values):

    temp=values[0][:4]
    values=[temp]

    newSample=[]
    newSample.append([])
    for k in range(len(values[0])):
        for j in range(k,len(values[0])):
            if k==j:
                continue
            newSample[0].append(values[0][k]/max(values[0][j],1e-5))
    
    
    scaled=scaler.transform(newSample)
 
    result1 = model1.predict(scaled).argmax()

    result2 = model2.predict(scaled)[0][0]
    result2_clipped = np.clip(result2, 0, 100) #rajataan arvo välille 0-100

    result4 = model4.predict(scaled)[0][0]
    result4_clipped = np.clip(result4, 0, 100) #rajataan arvo välille 0-100

    print('Malli1 (veikkaa luokka):',result1)
    print('Malli2 (veikkaa konsentraatiota):',result2_clipped, '(tulos ilman clippausta:',result2,')')
    print('Malli4 (veikkaa konsentraatiota):',result4_clipped, '(tulos ilman clippausta:', result4,')')
    print('Malli3 (veikkaa purkkia):', 'A' if model3.predict(scaled).argmax()==0 else 'B')

    return result1, result4_clipped

#test=np.array([[23636,16500,17438,21883]])

#GiveResult(test)