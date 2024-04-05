python -m pip install baidu-aip
python -m pip install opencv-python
python -m pip install cython
set path=%path%;%cd%\bin
cd models/research
setx pythonpath %cd%
setx PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION python
protoc object_detection/protos/*.proto --python_out=.
python -m pip install .
python -m install tensorflow_io
python -m pip install chardet
python -m pip install tensorflow
python -m pip install tf_slim
python -m pip install scipy
python -m pip install tf-models-official
python -m install tensorflow_io
python -m pip install --upgrade protobuf
echo 'building_environment.bat edited by Jackson Wong'
pause