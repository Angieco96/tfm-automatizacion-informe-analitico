<<<<<<< HEAD
# tfm-automatizacion-informe-analitico
Prototipo académico para la automatización de informes analíticos mediante procesamiento de datos e IA generativa.
=======
# Automatización de Informe Analítico con Azure OpenAI  
**Trabajo Fin de Máster – Visualización y Analítica de Datos Masivos**

---

## 1. Descripción general

Este proyecto desarrolla un prototipo de automatización del informe misional del proceso disciplinario, integrando técnicas de analítica de datos, generación automática de tablas y producción de texto descriptivo asistido por Inteligencia Artificial (Azure OpenAI).

La solución demuestra cómo un informe que tradicionalmente se elabora de forma manual puede ser generado de manera automática, manteniendo coherencia narrativa, control institucional del lenguaje y trazabilidad analítica.

El proyecto se presenta como Trabajo Fin de Máster (TFM) y tiene fines estrictamente académicos.

---

## 2. Objetivo del proyecto

El objetivo principal es diseñar e implementar una arquitectura que permita:

- Procesar información estructurada del proceso disciplinario.
- Construir automáticamente tablas analíticas en Python.
- Generar narrativas descriptivas institucionales mediante Azure OpenAI.
- Integrar tablas y texto en un documento Word (.docx) de forma automatizada.

El énfasis del proyecto se centra en la automatización del análisis y la generación de informes, no en la toma de decisiones ni en la emisión de recomendaciones.

---

## 3. Alcance y limitaciones

- El proyecto corresponde a un prototipo académico.
- No constituye una implementación productiva.
- No reemplaza procesos institucionales vigentes.
- La Inteligencia Artificial se utiliza exclusivamente con fines descriptivos, sin emitir juicios de valor, conclusiones o recomendaciones.

---

## 4. Arquitectura del proyecto

Estructura general del repositorio:

CUELLAR_OLANO_ANGIE_PAOLA_TFM/
│
├── config/                 Configuración de base de datos y Azure OpenAI  
│   ├── db_config.py  
│   └── openai_config.py  
│
├── data/                   Datos de ejemplo (anonimizados)  
│   └── sample_improd.csv  
│
├── plantillas/             Plantilla base del informe Word  
│   └── Plantilla_Prueba.docx  
│
├── prompts/                Prompts versionados (system y user)  
│   ├── prompt_total/  
│   ├── prompt_quejas/  
│   └── loader.py  
│
├── src/                    Lógica de negocio  
│   ├── tabla_niveldep.py  
│   ├── tabla_top.py  
│   ├── prompt_payloads.py  
│   ├── docx_utils.py  
│   └── utils.py  
│
├── tables/                 Consultas SQL  
│   └── consultas_sql.py  
│
├── salidas/                Informes generados  
│
├── main.ipynb              Orquestador principal del proceso  
├── requirements.txt  
└── README.md  

---

## 5. Datos utilizados

El archivo data/sample_improd.csv contiene datos anonimizados y transformados, diseñados únicamente para reproducir la estructura analítica del proceso disciplinario.

- Los identificadores han sido sustituidos y no corresponden a casos reales.
- No se incluyen nombres, personas investigadas, hechos ni decisiones.
- La información preserva exclusivamente variables analíticas como dependencia, nivel, año y clasificación de riesgo.

Este enfoque permite ejecutar el proyecto sin acceso a bases de datos institucionales reales.

---

## 6. Requisitos técnicos

Para ejecutar el proyecto se requiere:

- Python 3.9 o superior.
- Instalación de dependencias mediante el archivo requirements.txt.

Principales librerías utilizadas:

- pandas  
- numpy  
- matplotlib  
- sqlalchemy  
- pyodbc  
- openai (Azure OpenAI SDK)  
- python-docx  
- python-dotenv  

---

## 7. Configuración del entorno (.env)

Las credenciales no se incluyen en el repositorio.  
Cada usuario debe crear un archivo .env en la raíz del proyecto con la siguiente estructura:

DB_SERVER=xxxx  
DB_NAME=xxxx  
DB_USER=xxxx  
DB_PASSWORD=xxxx  
ODBC_DRIVER=ODBC Driver 17 for SQL Server  

AZURE_OPENAI_ENDPOINT=https://<tu-recurso>.openai.azure.com/  
AZURE_OPENAI_API_KEY=<tu_api_key>  
AZURE_OPENAI_API_VERSION=2024-02-15-preview  
AZURE_OPENAI_MODEL=<nombre_del_deployment>  

Nota:  
El proyecto puede ejecutarse sin conexión a base de datos, utilizando el CSV de ejemplo incluido.

---

## 8. Ejecución del proyecto

1. Abrir el archivo main.ipynb.
2. Ejecutar las celdas en orden.
3. El sistema realizará:
   - Carga y procesamiento de datos.
   - Construcción de tablas analíticas.
   - Generación de texto descriptivo mediante Azure OpenAI.
   - Inserción automática de tablas y texto en la plantilla Word.

El informe final se genera en la carpeta:

salidas/Informe_prueba.docx

---

## 9. Uso de Inteligencia Artificial

La Inteligencia Artificial se utiliza exclusivamente para:

- Transformar resultados numéricos en narrativas descriptivas.
- Mantener un tono institucional y analítico.
- Evitar recomendaciones, proyecciones o juicios de valor.

Los prompts están desacoplados del código y versionados para garantizar reproducibilidad, control narrativo y trazabilidad metodológica.

---

## 10. Consideraciones éticas y de gobierno de datos

- No se procesan datos personales ni sensibles.
- Los datos son anonimizados y no representan casos reales.
- Las credenciales se gestionan externamente mediante variables de entorno.
- El uso de IA está delimitado a fines descriptivos y académicos.

---

## 11. Autoría

Angie Cuellar Olano  
Trabajo Fin de Máster  
Máster en Visualización y Analítica de Datos Masivos  
Universidad Internacional de La Rioja (UNIR)
>>>>>>> cfa6ac5 (Proyecto TFM – estructura inicial y ejecución local)
