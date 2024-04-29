#! /bin/bash

BASEDIR=.

./corenlp-server.sh -quiet true -port 9000 -timeout 15000  &
sleep 1

# extract features
echo "Extracting features"
python3 extract-features.py $BASEDIR/data/devel/ > devel.cod &
python3 extract-features.py $BASEDIR/data/test/ > test.cod &

python3 extract-features.py $BASEDIR/data/train/ | tee train.cod | cut -f4- > train.cod.cl
python3 extract-features.py $BASEDIR/data/test/ | tee test.cod | cut -f4- > test.cod.cl

kill `cat /tmp/corenlp-server.running`

# train model
echo "Training model"
python3 train-sklearn.py model.joblib vectorizer.joblib < train.cod.cl
# run model
echo "Running model..."
python3 predict-sklearn.py model.joblib vectorizer.joblib < devel.cod > devel.out
python3 predict-sklearn.py model.joblib vectorizer.joblib < test.cod > test.out

# evaluate results
echo "Evaluating results..."
python3 evaluator.py DDI $BASEDIR/data/devel/ devel.out > devel.stats
python3 evaluator.py DDI $BASEDIR/data/test/ test.out > test.stats

