#!/bin/bash

# Paste yt-spotDL_MD folder location here
cd /mnt/2A285F00285ECB09/Tool_Scripts/yt-spotDL_MD

# Launches terminal for music downloading process
gnome-terminal -- bash -c "source venv/bin/activate; python3 main_screen.py"
