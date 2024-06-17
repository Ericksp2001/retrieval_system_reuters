# Instrucciones de uso
* Entorno virtual
Inmediatamente despues de clonar el repositorio es necesario crear un entorno virtual de python
```bash
python -m venv env
```
Luego debemos activarlo de la siguiente forma:
```bash
env\Scripts\activate
```
Ahora debemos instalar las librerias necesarias que se encuentran listadas en el archivo requirements.txt
```bash
pip install -r requirements.txt
```
* Generacion de archivos Joblib
Ahora dado que existe una limitacion en el tamaño de los archivos que se puedes subir a github, se deben de
generar los objetos joblib para esto se debe de ejecutar una vez todo el notebook. Para esto debemos de activar el kernel
perteneciente al entorno virtual recien creado.
  * En la parte superior derecha se encuentra un icono "Seleccionar kernel"
  * Luego, seleccionamos "Entornos de Python"
  * Seleccionamos "emv/Scripts/python.exe" o similar
Ahora ya podemos ejecutar el notebook 
* Iniciar la API
Para que el frontend pueda funcionar se debe de correr la API

**⚠️ ¡Advertencia!**
A partir de la creacion del entorno virtual este mismo siempre debe de estar activo
