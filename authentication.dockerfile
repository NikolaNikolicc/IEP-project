FROM python:3

# -p garantuje da ce sve sto ne postoji na putanji da se kreira
RUN mkdir -p /opt/src/UserAuthentication
# svaka naredna naredba se izvrsava relativno u odnosu na ovaj direktorijum
WORKDIR /opt/src/UserAuthentication

#    putanja_od    kopiramo u tekuci direktorijum u fajl:
COPY UserAuthentication/application.py ./application.py
COPY UserAuthentication/configuration.py ./configuration.py
COPY UserAuthentication/models.py ./models.py
COPY UserAuthentication/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

# ENTRYPOINT ["echo", "hello world"]
# ENTRYPOINT ["sleep", "1200"]

ENV PYTHONPATH="/opt/src/UserAuthentication"

ENTRYPOINT ["python", "./application.py"]