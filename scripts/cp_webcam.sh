# Run this script via root cronjob every minute
# SSH authentication via public key
rsync -avzh -e ssh /home/zielke/SolarPy/templates/public/webcam/ root@192.168.15.107:/var/www/html/webcam/

