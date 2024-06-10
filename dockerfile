# Utilizar la imagen base de Python 3.11.6
FROM python:3.11.6-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar los archivos requirements.txt al contenedor
COPY requirement.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirement.txt

# Copiar el contenido del proyecto al contenedor
COPY . .

# Exponer el puerto en el que la aplicación correrá
EXPOSE 5000

# Definir la variable de entorno para que Flask corra en el modo de producción
ENV FLASK_ENV=production

# Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]