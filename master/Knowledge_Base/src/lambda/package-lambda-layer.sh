python3 -m venv create_layer
source create_layer/bin/activate
pip install -r requirements.txt
echo create_layer venv created and dependencies install

mkdir python
cp -r create_layer/lib python/
zip -r layer_content.zip python
echo create_layer venv copied to python dir and zipped
