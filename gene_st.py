import streamlit as st
import pandas as pd
from io import BytesIO
import requests
base_text=""



url = 'https://raw.githubusercontent.com/jesusiv24921/app_ilt/main/20230709_ILT_BASE.txt'

try:
    response = requests.get(url)
    response.raise_for_status()
    with open('20230709_ILT_BASE.txt', 'wb') as file:
        file.write(response.content)
except requests.exceptions.RequestException as e:
    print(f"Error al descargar el archivo: {e}")
except Exception as e:
    print(f"Error: {e}")

# Ahora puedes abrir el archivo local
with open('20230709_ILT_BASE.txt', 'r') as base_file:
    base_text=base_file.read()



    

st.title("ILT DATA GENERATOR")

st.sidebar.header("Settings")
nuevo_well=st.sidebar.text_input("Well Name", "CAN420")
nuevo_uwi=st.sidebar.text_input("UWI Name", "CAN420")
nueva_fecha=st.sidebar.text_input("Date", "09/07/2023")

file=st.file_uploader("Upload a CSV file", type=["csv"])

generate_txt_button=st.button

if file is not None:
    df=pd.read_csv(file,sep=";")
    df=df.dropna()
    
    nuevo_tope=int(df['Tope'].min()-10)
    nueva_base=int(df['Base'].max()+10)

    nuevos_valores=list(range(nuevo_tope, nueva_base+1))

    st.header("Generated Data")
    st.write("Updated Well:", nuevo_well)
    st.write("Updated UWI:", nuevo_uwi)
    st.write("Updated DATE:", nueva_fecha)

    nuevos_valores=list(range(nuevo_tope, nueva_base+1))
    df_new=pd.DataFrame({'Depth':nuevos_valores})
    df_new["Z1"]=df_new['Depth'].apply(lambda x: df.loc[(x>=df['Tope']) & (x<=df['Base']), '14/4/2023'].values[0] if any(((x>=df['Tope']) & (x<=df['Base'])))else 0.00)

    df_new['Z2']=[0.00 for i in range(len(df_new))]
    df_new['Z3']=df_new["Z1"]
    df_new['Z4']=[0.00 for i in range(len(df_new))]

    df_new['Z2']=(df_new['Z2'])
    df_new['Z3']=df_new["Z1"]
    df_new['Z4']=[0 for i in range(len(df_new))]

    df_new=df_new.astype(str)

    df_new=df_new.apply(lambda x:x.str.replace('.',','))

    st.dataframe(df_new)

    if generate_txt_button:
        output=BytesIO()

        lineas=base_text.split('\n')

        for i, linea in enumerate(lineas):
            if "WELL." in linea:
                lineas[i]=f'WELL. {nuevo_well}:WELL'
            
            elif "UWI." in linea:
                lineas[i]=f'UWI. {nuevo_uwi}:UNIQUE WELL ID'
            
            elif "DATE." in linea:
                lineas[i]=f'DATE. {nueva_fecha}:DATE'
    
            #Encuentra la linea que contiene ""~$ILT CAN700.xlsm"
        indice_inicio_seccion=None

        for i, linea in enumerate(lineas):
            if "~A" in linea:
                indice_inicio_seccion=i
                break
            #Remplazar las lineas actualizadas con el Dataframe

        if indice_inicio_seccion is not None:
            df_lines=df_new.apply(lambda row:'\t'.join(row.astype(str)),axis=1).to_list()
            # df_lines=['\n'.join(df_lines[i:i+4]) for i in range(0,len(df_lines),4)]
            # df_lines=df_new.to_string(header=False, index=False).split('\n')[1:]
            lineas[indice_inicio_seccion+1:indice_inicio_seccion+1+len(df_lines)]=df_lines
            

        output.write("\n".join(lineas).encode())
        output.seek(0)

        st.success("nuevo.txt generated!")

        st.subheader("Dowload nuevo.txt")
        st.write("Click the button")
        st.download_button(
            label="Dowload",
            data=output,
            key="Dowload",
            file_name="nuevo.txt"

        )




