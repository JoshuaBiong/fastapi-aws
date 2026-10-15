# Future Features

## systemd setup (replace nohup)

SSH into EC2 and run:

```bash
sudo tee /etc/systemd/system/notesapp.service << 'EOF'
[Unit]
Description=Notes App
After=network.target

[Service]
ExecStart=/home/ec2-user/.local/bin/uv run fastapi run main.py --host 0.0.0.0 --port 8000
WorkingDirectory=/home/ec2-user/fastapi-aws
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF
```

Then:

```bash
sudo kill $(sudo lsof -t -i:8000)
sudo systemctl daemon-reload
sudo systemctl enable notesapp
sudo systemctl start notesapp
```

Commands:

```bash
sudo systemctl status notesapp    # check status
sudo systemctl stop notesapp      # stop
sudo systemctl start notesapp     # start
sudo systemctl restart notesapp   # restart
journalctl -u notesapp -f         # view logs live
```
