import requests
import streamlit as st
import pandas as pd

import csv
import tempfile

url = 'https://raw.githubusercontent.com/jesusiv24921/app_ilt/main/20230709_ILT_BASE.txt'

try:
    # Realiza una solicitud GET para obtener el contenido del archivo
    response = requests.get(url)
    response.raise_for_status()

    # Lee el contenido del archivo directamente desde la respuesta
    base_text = response.text

except requests.exceptions.RequestException as e:
    st.error(f"Error al obtener el archivo desde GitHub: {e}")
except Exception as e:
    st.error(f"Error: {e}")

st.title("PLT-ILT DATA GENERATOR")

st.sidebar.header("Settings")


file = st.file_uploader("Upload a CSV file", type=["csv"])
file_1=file
# Agregar un radio button para seleccionar entre "plt" e "ilt"
opcion_seleccionada = st.radio("Seleccionar opción:", ("PLT", "ILT"))

# Guardar el nombre correspondiente en una variable
if opcion_seleccionada == "PLT":
    nombre_seleccionado = "PLT"
else:
    nombre_seleccionado = "ILT"


generate_txt_button = st.button("Generate Text File")



if file is not None:
    df_1 = pd.read_csv(file, sep=',', header=None)
    st.write(len(df_1.columns))
    st.write(type(len(df_1.columns)))
    
    if len(df_1.columns)==6:
        df = pd.read_csv(file_1, sep=',', header=None)
    else:
        df = pd.read_csv(file_1, sep=';', header=None)
    
    st.write(df)
    st.write(len(df.columns))
    df_=df.iloc[0:2,0:2]
    st.write(df_)
    df=df.drop([0,1], axis=0).reset_index(drop=True)
    st.write(df)
    df.columns=df.iloc[0]
    st.write(df)
    df = df.drop(0).reset_index(drop=True)
    st.write(df)
    nombre_pozo=df_.iloc[0,1]
    fecha_registro=df_.iloc[1,1]
    fecha_registro = pd.to_datetime(fecha_registro)
    nuevo_well = st.sidebar.text_input("Name_1", nombre_pozo, disabled=True)
    nuevo_uwi = st.sidebar.text_input("Name_2", nombre_pozo, disabled=True)
    nueva_fecha = st.sidebar.text_input("Date", fecha_registro, disabled=True)

    archivo_salida = st.sidebar.text_input("name txt (YYYYMMDD_ILT_Name_1.txt)", f"{fecha_registro.year}{fecha_registro.month}{fecha_registro.day}_{nombre_seleccionado}_{nombre_pozo}.txt", disabled=True)



    df = df.dropna()
    df['Tope']=df['Tope'].astype(int)
    df['Base']=df['Base'].astype(int)
    nuevo_tope = int(df['Tope'].min() - 10)
    nueva_base = int(df['Base'].max() + 10)

    # nuevo_tope = (df['Tope'].min() - 10)
    # nueva_base = (df['Base'].max() + 10)

    nuevos_valores = list(range(nuevo_tope, nueva_base + 1))

    st.header("Generated Data")
    st.write("Updated Well:", nuevo_well)
    st.write("Updated UWI:", nuevo_uwi)
    st.write("Updated DATE:", nueva_fecha)
    

    nuevos_valores = list(range(nuevo_tope, nueva_base + 1))
    df_new = pd.DataFrame({'Depth': nuevos_valores})
    df_new["Z1"] = df_new['Depth'].apply(lambda x: df.loc[(x >= df['Tope']) & (x <= df['Base']), 'Ql.bbl/d'].values[0] if any(((x >= df['Tope']) & (x <= df['Base']))) else 0.00)

    df_new['Z2'] = df_new['Depth'].apply(lambda x: df.loc[(x >= df['Tope']) & (x <= df['Base']), 'Qo.bbl/d'].values[0] if any(((x >= df['Tope']) & (x <= df['Base']))) else 0.00)
    df_new['Z3'] = df_new['Depth'].apply(lambda x: df.loc[(x >= df['Tope']) & (x <= df['Base']), 'Qw.bbl/d'].values[0] if any(((x >= df['Tope']) & (x <= df['Base']))) else 0.00)
    df_new['Z4'] = [0.00 for _ in range(len(df_new))]

    df_new = df_new.astype(str)
    df_new = df_new.apply(lambda x: x.str.replace('.', ','))
    # nuevo_tope1=str(nuevo_tope)
    # nueva_base1=str(nueva_base)
    nuevo_tope1 = st.sidebar.text_input("Top", nuevo_tope+10,disabled=True)
    nueva_base1 = st.sidebar.text_input("Bottom", nueva_base-10,disabled=True)
    

    # st.table(df_new)

    if generate_txt_button:
        # Procesa el archivo base_text directamente
        if base_text:
            lines = base_text.split('\n')

            for i, linea in enumerate(lines):
                if "WELL." in linea:
                    lines[i] = f'WELL. {nuevo_well}:WELL'
                elif "UWI." in linea:
                    lines[i] = f'UWI. {nuevo_uwi}:UNIQUE WELL ID'
                elif "DATE." in linea:
                    lines[i] = f'DATE. {nueva_fecha}:DATE'
                elif "STRT.F" in linea:
                    lines[i]=f'STRT.F {nuevo_tope+10}:START DEPTH'
                elif "STOP.F" in linea:
                    lines[i]=f'STOP.F {nueva_base-10}:STOP DEPTH'

            

            # Encuentra la línea que contiene "~A" para reemplazar la sección adecuada
            indice_inicio_seccion = None

            for i, linea in enumerate(lines):
                if "~A" in linea:
                    indice_inicio_seccion = i
                    break

            # Remplaza las líneas actualizadas con el DataFrame
            if indice_inicio_seccion is not None:
                df_lines = df_new.apply(lambda row: '\t'.join(row.astype(str)), axis=1).to_list()
                lines[indice_inicio_seccion + 1:indice_inicio_seccion + 1 + len(df_lines)] = df_lines

            st.success("nuevo.txt generated")

            st.subheader("Download nuevo.txt")
            st.write("Click the button")
            st.download_button(
                label="Download",
                data="\n".join(lines),
                key="Download",
                file_name=archivo_salida,
            )
