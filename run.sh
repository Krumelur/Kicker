#!/bin/bash
# IMPORTANT: For the game to autostart, run 'sudo chmod +x run.sh' in the terminal.
#            Then add the line '@lxterminal /home/pi/Documents/Develop/Kicker/run.sh' to
#            the file '/etc/xdg/lxsession/LXDE-pi/autostart'.
cd /home/pi/Documents/Develop/Kicker/src
python -m venv defaultenv
source defaultenv/bin/activate
pip install -r ../requirements.txt
python main.py