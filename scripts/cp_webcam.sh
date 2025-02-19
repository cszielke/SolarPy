# Run this script via root cronjob every minute
# SSH authentication via public key
# Generate Key with        ssh-keygen -f ~/.ssh/id_rsa -q -P ""
# Show Key with            cat ~/.ssh/id_rsa.pub
# Copy key in Target       ~/.ssh/authorized_keys
# Restart sshd in Target   service ssh restart
rsync -avzh -e ssh /home/zielke/SolarPy/templates/public/webcam/ root@192.168.15.241:/var/www/html/webcam/

