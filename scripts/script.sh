python ../detector/model.py
python -m spacy init fill-config ../config/base_config.cfg ../config/config.cfg
python -m spacy train ../config/config.cfg --output ../output