mkdir -p $HOME/.config/systemd/user/

echo '[Unit]
Description="Lazerpaw cat lazer chase game"
After=pigpiod.service
Wants=pigpiod.service

[Service]
WorkingDirectory='$(pwd)'
ExecStart=python3 '$(pwd)'/lazerpaw.py
StandardError=null
Restart=always

[Install]
WantedBy=default.target' > $HOME/.config/systemd/user/chatbox.service