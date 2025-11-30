# Proyecto-GRIA-USC
Este repositorio corresponde a la arquitectura base del proyecto para el Grado en Inteligencia Artificial (USC) en colaboración con Balidea.

### Versión de Python: 3.11

## Backend
El backend sigue la siguiente estructura:

* **api**: define los endpoints del API REST de FastAPI.
* **service**: define la lógica de negocio de la aplicación para los distintos módulos.
* **core**: define el flujo principal del agente.
* **config**: define la configuración del sistema.

El fichero `.env.example` contiene ejemplos de las variables de entorno que se pueden necesitar en el sistema. Se debe crear un fichero `.env` en su lugar.

Comando para instalar las librerías necesarias:
```
pip install -r requirements.txt
```

Comando para ejecutar la aplicación:

```
fastapi dev wsgi.py
```

## Frontend
El frontend sigue la siguiente estructura:

* **api**: define los endpoints que atacan a la API del backend.
* **pages**: define las vistas de la interfaz.

Comando para instalar las librerías necesarias:
```
pip install -r requirements.txt
```

Comando para ejecutar la aplicación:

```
streamlit run app.py
```
