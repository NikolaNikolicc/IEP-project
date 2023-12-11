FROM python:3

# -p garantuje da ce se kreirati sve sto ne postoji na putanji
RUN mkdir -p /opt/src/UserAuthentication
# svaka naredna naredba se izvrsava relativno u odnosu na ovaj direktorijum
WORKDIR /opt/src/UserAuthentication

#    putanja_od    kopiramo u tekuci direktorijum u fajl:
COPY UserAuthentication/migrate.py ./migrate.py
COPY UserAuthentication/configuration.py ./configuration.py
COPY UserAuthentication/models.py ./models.py
COPY UserAuthentication/requirements.txt ./requirements.txt

# instaliraj sve sto je potrebno na kontejneru
RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/UserAuthentication"

# naredba za pokretanje kontejnera
ENTRYPOINT ["python", "./migrate.py"]