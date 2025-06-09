FROM python:3.9

WORKDIR /app

# Instala dependências do sistema necessárias para mysqlclient
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]
