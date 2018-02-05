# minerrestarter



### FAQ
#### How do I stop windows from asking me if it's ok to run stak-xmr ?
https://superuser.com/questions/850473/giving-permission-to-program-to-run-with-out-confirmation-in-start-command-windo



### Building in windows
Download & install python3.7
python -m pip install PyInstaller
cd <minerrestarter directory>
python -m PyInstaller minerrestarter.py --clean -y -F --uac-admin
