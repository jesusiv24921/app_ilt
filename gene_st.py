import requests
import streamlit as st
import pandas as pd

# URL del archivo en GitHub
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

st.title("ILT DATA GENERATOR")

st.sidebar.header("Settings")
nuevo_well = st.sidebar.text_input("Well Name", "CAN420")
nuevo_uwi = st.sidebar.text_input("UWI Name", "CAN420")
nueva_fecha = st.sidebar.text_input("Date", "09/07/2023")

file = st.file_uploader("Upload a CSV file", type=["csv"])

generate_txt_button = st.button("Generate Text File")

if file is not None:
    df = pd.read_csv(file, sep=";")
    df = df.dropna()
    
    nuevo_tope = int(df['Tope'].min() - 10)
    nueva_base = int(df['Base'].max() + 10)

    nuevos_valores = list(range(nuevo_tope, nueva_base + 1))

    st.header("Generated Data")
    st.write("Updated Well:", nuevo_well)
    st.write("Updated UWI:", nuevo_uwi)
    st.write("Updated DATE:", nueva_fecha)

    nuevos_valores = list(range(nuevo_tope, nueva_base + 1))
    df_new = pd.DataFrame({'Depth': nuevos_valores})
    df_new["Z1"] = df_new['Depth'].apply(lambda x: df.loc[(x >= df['Tope']) & (x <= df['Base']), '14/4/2023'].values[0] if any(((x >= df['Tope']) & (x <= df['Base']))) else 0.00)

    df_new['Z2'] = [0.00 for _ in range(len(df_new))]
    df_new['Z3'] = df_new["Z1"]
    df_new['Z4'] = [0.00 for _ in range(len(df_new))]

    df_new['Z2'] = (df_new['Z2'])
    df_new['Z3'] = df_new["Z1"]
    df_new['Z4'] = [0 for _ in range(len(df_new))]

    df_new = df_new.astype(str)

    df_new = df_new.apply(lambda x: x.str.replace('.', ','))

    st.dataframe(df_new)

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

            st.success("nuevo.txt generated!")

            st.subheader("Download nuevo.txt")
            st.write("Click the button")
            st.download_button(
                label="Download",
                data="\n".join(lines),
                key="Download",
                file_name="nuevo.txt",
            )




