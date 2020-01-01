update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2
# update-alternatives --config python
sudo apt install python3-venv python3-pip
python3 -m pip install --user virtualenv
python3 -m venv env
source env/bin/activate
#Installs for Pillow
sudo apt install libwebp6 libtiff5 libjbig0 liblcms2-2 libwebpmux3 libopenjp2-7 libzstd1 libwebpdemux2
pip install mod_wsgi-standalone
pip install -r requirements.txt
