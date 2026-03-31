import pandas as pd
import pathlib
import numpy as np


def get_current_file_path():     
    file_path = str(pathlib.Path(__file__).parent.resolve())  +'\\'   
    return file_path

def GetDfAll(noiseAmount=0):

    allFiles=[]

    #Jokaisen labelin failit omalla appendilla
    allFiles.append(['vesi_A_SLOT_0','vesi_A_SLOT_1','vesi_A_SLOT_2','vesi_A_SLOT_3'])
    allFiles.append(['vesi_B_SLOT_0','vesi_B_SLOT_1','vesi_B_SLOT_2','vesi_B_SLOT_3'])

    allFiles.append(['hemo_12_5_A_SLOT_0','hemo_12_5_A_SLOT_1','hemo_12_5_A_SLOT_2','hemo_12_5_A_SLOT_3'])
    allFiles.append(['hemo_12_5_B_SLOT_0','hemo_12_5_B_SLOT_1','hemo_12_5_B_SLOT_2','hemo_12_5_B_SLOT_3'])

    allFiles.append(['hemo_25_A_SLOT_0','hemo_25_A_SLOT_1','hemo_25_A_SLOT_2','hemo_25_A_SLOT_3'])
    allFiles.append(['hemo_25_B_SLOT_0','hemo_25_B_SLOT_1','hemo_25_B_SLOT_2','hemo_25_B_SLOT_3'])
    
    allFiles.append(['hemo_50_A_SLOT_0','hemo_50_A_SLOT_1','hemo_50_A_SLOT_2','hemo_50_A_SLOT_3'])
    allFiles.append(['hemo_50_B_SLOT_0','hemo_50_B_SLOT_1','hemo_50_B_SLOT_2','hemo_50_B_SLOT_3'])

    allFiles.append(['hemo_100_A_SLOT_0','hemo_100_A_SLOT_1','hemo_100_A_SLOT_2','hemo_100_A_SLOT_3'])
    allFiles.append(['hemo_100_B_SLOT_0','hemo_100_B_SLOT_1','hemo_100_B_SLOT_2','hemo_100_B_SLOT_3'])


    dfAll=pd.DataFrame() 
    for i in range(len(allFiles[0])):
        dfAll['S'+str(i)] = None

    def AntaaLabelDf(files,files2, y):
        dfLabel=pd.DataFrame(columns=dfAll.columns)

        for i in range(len(files)):
            dfArr=pd.read_csv(get_current_file_path()+'/raw/'+files[i]+'.txt', delimiter= ';',header=None)
            dfArr2=pd.read_csv(get_current_file_path()+'/raw/'+files2[i]+'.txt', delimiter= ';',header=None)
            #dfLabel[dfLabel.columns[i]]=dfArr[dfArr.columns[1]]
            dfLabel[dfLabel.columns[i]]=pd.concat([dfArr[dfArr.columns[1]],dfArr2[dfArr2.columns[1]]])


        dfLabel['Y']=y
        return dfLabel


    labelLists=[]

    for i in range(0,len(allFiles),2):
        labelLists.append(AntaaLabelDf(allFiles[i],allFiles[i+1],int(i/2)))

    
    dfAll=pd.concat(labelLists)
    
    dfAll.dropna(inplace=True)

    dfAll.reset_index(drop=True, inplace=True)

    #dfAll.to_csv(get_current_file_path()+"AllData.csv", index=False)

    if noiseAmount>0:
        stds=dfAll.std().values
        for i in range(len(dfAll.columns)-1):
            rnd = np.random.uniform(low=-stds[i]*noiseAmount, high=stds[i]*noiseAmount,size=(dfAll.shape[0]))
            dfAll[dfAll.columns[i]]+=rnd
        

    return dfAll


def GetDfAllSynt(noiseAmount=0,df=None ):
    if not isinstance(df, pd.DataFrame):
        dfAll=GetDfAll(noiseAmount)
    else:
        dfAll=df

    dfNew=pd.DataFrame()
    for i in range(len(dfAll.columns)-1):
        for j in range(i,len(dfAll.columns)-1):
            if i==j:
                continue
            dfNew['S'+str(i)+'/S'+str(j)]=dfAll['S'+str(i)]/dfAll['S'+str(j)]

    dfNew['Y']=dfAll['Y']
    
    #dfNew.to_csv("AllDataSynt.csv", index=False)
    return dfNew

def GetHPFiltered(noiseAmount=0):

    dfAll=GetDfAll(noiseAmount)

    lbls=[]
    lbls.append(dfAll[dfAll['Y']==0])
    lbls.append(dfAll[dfAll['Y']==1])

    """
    High-pass filter via exponential moving average subtraction

    signal : 1D numpy array
    fs     : sampling rate (Hz)
    fc     : cutoff frequency (Hz)
    """
    fs=2458 
    fc=5
    dt = 1.0 / fs
    tau = 1.0 / (2 * np.pi * fc)
    beta = dt / (tau + dt)
    #print(dfAll.columns[0])

    for j in range(2):
        for k in range(3): 
            signal=lbls[j][lbls[j].columns[k]]
            avg = 0.0
            y = np.zeros_like(signal, dtype=float)

            for i, x in enumerate(signal):
                avg += beta * (x - avg)
                y[i] = x - avg


            lbls[j][lbls[j].columns[k]]=y

    dfNew=pd.concat(lbls)
    
    dfNew=GetDfAllSynt(noiseAmount,dfNew)

    return dfNew


def GetDfAllSyntPurkit():

    allFiles=[]

    #Jokaisen labelin failit omalla appendilla
    allFiles.append(['vesi_A_SLOT_0','vesi_A_SLOT_1','vesi_A_SLOT_2','vesi_A_SLOT_3'])
    allFiles.append(['vesi_B_SLOT_0','vesi_B_SLOT_1','vesi_B_SLOT_2','vesi_B_SLOT_3'])

    allFiles.append(['hemo_12_5_A_SLOT_0','hemo_12_5_A_SLOT_1','hemo_12_5_A_SLOT_2','hemo_12_5_A_SLOT_3'])
    allFiles.append(['hemo_12_5_B_SLOT_0','hemo_12_5_B_SLOT_1','hemo_12_5_B_SLOT_2','hemo_12_5_B_SLOT_3'])

    allFiles.append(['hemo_25_A_SLOT_0','hemo_25_A_SLOT_1','hemo_25_A_SLOT_2','hemo_25_A_SLOT_3'])
    allFiles.append(['hemo_25_B_SLOT_0','hemo_25_B_SLOT_1','hemo_25_B_SLOT_2','hemo_25_B_SLOT_3'])
    
    allFiles.append(['hemo_50_A_SLOT_0','hemo_50_A_SLOT_1','hemo_50_A_SLOT_2','hemo_50_A_SLOT_3'])
    allFiles.append(['hemo_50_B_SLOT_0','hemo_50_B_SLOT_1','hemo_50_B_SLOT_2','hemo_50_B_SLOT_3'])

    allFiles.append(['hemo_100_A_SLOT_0','hemo_100_A_SLOT_1','hemo_100_A_SLOT_2','hemo_100_A_SLOT_3'])
    allFiles.append(['hemo_100_B_SLOT_0','hemo_100_B_SLOT_1','hemo_100_B_SLOT_2','hemo_100_B_SLOT_3'])


    dfAll=pd.DataFrame() 
    for i in range(len(allFiles[0])):
        dfAll['S'+str(i)] = None


    def AntaaLabelDf(files, y):
        dfLabel=pd.DataFrame(columns=dfAll.columns)

        for i in range(4):

            dfArr1=pd.read_csv(get_current_file_path()+'/raw/'+allFiles[y][i]+'.txt', delimiter= ';',header=None)
            dfArr2=pd.read_csv(get_current_file_path()+'/raw/'+allFiles[y+2][i]+'.txt', delimiter= ';',header=None)
            dfArr3=pd.read_csv(get_current_file_path()+'/raw/'+allFiles[y+4][i]+'.txt', delimiter= ';',header=None)
            dfArr4=pd.read_csv(get_current_file_path()+'/raw/'+allFiles[y+6][i]+'.txt', delimiter= ';',header=None)
            dfArr5=pd.read_csv(get_current_file_path()+'/raw/'+allFiles[y+8][i]+'.txt', delimiter= ';',header=None)

            dfArr1.drop([0,2],axis=1,inplace=True)
            dfArr2.drop([0,2],axis=1,inplace=True)
            dfArr3.drop([0,2],axis=1,inplace=True)
            dfArr4.drop([0,2],axis=1,inplace=True)
            dfArr5.drop([0,2],axis=1,inplace=True)

            dfLabel[dfLabel.columns[i]]=pd.concat([dfArr1,dfArr2,dfArr3,dfArr4,dfArr5])


        dfLabel['Y']=y
        return dfLabel


    labelLists=[]

    for i in range(2):
        labelLists.append(AntaaLabelDf(allFiles[0],i))

    
    dfAll=pd.concat(labelLists)
    
    dfAll.dropna(inplace=True)

    dfAll.reset_index(drop=True, inplace=True)

    dfAll.to_csv(get_current_file_path()+"AllDataPurkit.csv", index=False)



    return GetDfAllSynt(0,dfAll )

