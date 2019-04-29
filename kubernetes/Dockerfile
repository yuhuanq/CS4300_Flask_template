# Read from Ubuntu Base Image
FROM python:3
RUN mkdir -p /service
# Copy over all the files of interest
ADD app /service/app
ADD songs.json /service/songs.json
ADD annotation_to_fragment.p /service/annotation_to_fragment.p
ADD annotation_to_song.p /service/annotation_to_song.p
ADD annotation_to_text.p /service/annotation_to_text.p
ADD song_to_name.p /service/song_to_name.p
ADD app.py /service/app.py
ADD config.py /service/config.py
ADD manage.py /service/manage.py
ADD requirements.txt /service/requirements.txt
WORKDIR /service/
RUN pip install -r requirements.txt
CMD python -u app.py $APP_SETTINGS $DATABASE_URL
