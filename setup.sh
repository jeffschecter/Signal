pip install WebTest

SITE_PACKAGES=`python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`
echo "/usr/local/google_appengine" > $SITE_PACKAGES/appengine.pth

APP_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
echo $APP_DIR > $SITE_PACKAGES/signal_app.pth
