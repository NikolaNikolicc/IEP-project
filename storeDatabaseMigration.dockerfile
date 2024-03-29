FROM python:3

# -p garantuje da ce se kreirati sve sto ne postoji na putanji
RUN mkdir -p /opt/src/Store
# svaka naredna naredba se izvrsava relativno u odnosu na ovaj direktorijum
WORKDIR /opt/src/Store

#    putanja_od    kopiramo u tekuci direktorijum u fajl:
COPY Store/migrate.py ./migrate.py
COPY Store/configuration.py ./configuration.py
COPY Store/models.py ./models.py
COPY Store/requirements.txt ./requirements.txt

# instaliraj sve sto je potrebno na kontejneru
RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/Store"

# naredba za pokretanje kontejnera
ENTRYPOINT ["python", "./migrate.py"]