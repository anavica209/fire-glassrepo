# 1. Usamos una imagen oficial y ligera de Python
FROM python:3.11-slim

# 2. Establecemos la carpeta de trabajo dentro del contenedor
WORKDIR /code

# 3. Copiamos e instalamos las dependencias primero
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiamos el código de la aplicación y la carpeta data
# Copiamos TODO el proyecto (app, static, templates, data, etc.)
COPY . .

# 5. Exponemos el puerto donde correrá la app
EXPOSE 8000

# 6. Comando para iniciar el servidor (Elige la opción según tu framework):

# OPCIÓN A: Si usas FastAPI con Uvicorn (descomenta o deja esta línea)
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]

# OPCIÓN B: Si usas Flask, borra la línea de arriba y usa esta:
# CMD ["python", "-m", "flask", "--app", "app.main", "run", "--host=0.0.0.0", "--port=8000"]
