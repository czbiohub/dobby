# dobby
Dobby is the heroic house-elf that automates SampleSheet generation from Google Sheets


## Setup

To set up the Google Drive API, these are the steps we took.

### 1. Installation of
[`google-drive-ocamlfuse`](http://www.omgubuntu.co.uk/2017/04/mount-google-drive-ocamlfuse-linux)

```
utility@ds06:~$ sudo add-apt-repository ppa:alessandro-strada/ppa
[sudo] password for utility: 
Sorry, try again.
[sudo] password for utility: 
 Mount Google Drive on Ubuntu (via FUSE)
 More info: https://launchpad.net/~alessandro-strada/+archive/ubuntu/ppa
Press [ENTER] to continue or ctrl-c to cancel adding it

gpg: keyring `/tmp/tmpasgt1i04/secring.gpg' created
gpg: keyring `/tmp/tmpasgt1i04/pubring.gpg' created
gpg: requesting key F639B041 from hkp server keyserver.ubuntu.com
gpg: /tmp/tmpasgt1i04/trustdb.gpg: trustdb created
gpg: key F639B041: public key "Launchpad PPA for Alessandro Strada" imported
gpg: Total number processed: 1
gpg:               imported: 1  (RSA: 1)
OK
utility@ds06:~$ sudo apt update && sudo apt install google-drive-ocamlfuse
Hit:1 http://us.archive.ubuntu.com/ubuntu xenial InRelease
Get:2 http://us.archive.ubuntu.com/ubuntu xenial-updates InRelease [102 kB]                   
Get:3 http://security.ubuntu.com/ubuntu xenial-security InRelease [102 kB]                              
Get:4 http://ppa.launchpad.net/alessandro-strada/ppa/ubuntu xenial InRelease [17.5 kB]    
Get:5 http://us.archive.ubuntu.com/ubuntu xenial-backports InRelease [102 kB]                            
Get:6 http://ppa.launchpad.net/alessandro-strada/ppa/ubuntu xenial/main amd64 Packages [1,368 B]                    
Get:7 http://us.archive.ubuntu.com/ubuntu xenial-updates/main amd64 Packages [620 kB]                                
Get:8 http://ppa.launchpad.net/alessandro-strada/ppa/ubuntu xenial/main i386 Packages [1,372 B]                   
Get:9 http://ppa.launchpad.net/alessandro-strada/ppa/ubuntu xenial/main Translation-en [932 B]       
Get:10 http://us.archive.ubuntu.com/ubuntu xenial-updates/main i386 Packages [596 kB]       
Get:11 http://security.ubuntu.com/ubuntu xenial-security/main amd64 Packages [344 kB]
Get:12 http://us.archive.ubuntu.com/ubuntu xenial-updates/main Translation-en [251 kB]    
Get:13 http://us.archive.ubuntu.com/ubuntu xenial-updates/main amd64 DEP-11 Metadata [304 kB]
Get:14 http://us.archive.ubuntu.com/ubuntu xenial-updates/main DEP-11 64x64 Icons [207 kB]     
Get:15 http://us.archive.ubuntu.com/ubuntu xenial-updates/universe amd64 Packages [517 kB]
Get:16 http://us.archive.ubuntu.com/ubuntu xenial-updates/universe i386 Packages [497 kB]
Get:17 http://us.archive.ubuntu.com/ubuntu xenial-updates/universe amd64 DEP-11 Metadata [171 kB]
Get:18 http://us.archive.ubuntu.com/ubuntu xenial-updates/universe DEP-11 64x64 Icons [226 kB]
Get:19 http://us.archive.ubuntu.com/ubuntu xenial-updates/multiverse amd64 DEP-11 Metadata [5,892 B]
Get:20 http://us.archive.ubuntu.com/ubuntu xenial-backports/main amd64 DEP-11 Metadata [3,328 B]
Get:21 http://us.archive.ubuntu.com/ubuntu xenial-backports/universe amd64 DEP-11 Metadata [5,132 B]
Get:22 http://security.ubuntu.com/ubuntu xenial-security/main i386 Packages [323 kB]        
Get:23 http://security.ubuntu.com/ubuntu xenial-security/main amd64 DEP-11 Metadata [60.0 kB]
Get:24 http://security.ubuntu.com/ubuntu xenial-security/main DEP-11 64x64 Icons [52.1 kB]
Get:25 http://security.ubuntu.com/ubuntu xenial-security/universe amd64 Packages [156 kB]
Get:26 http://security.ubuntu.com/ubuntu xenial-security/universe i386 Packages [137 kB]
Get:27 http://security.ubuntu.com/ubuntu xenial-security/universe amd64 DEP-11 Metadata [48.8 kB]
Get:28 http://security.ubuntu.com/ubuntu xenial-security/universe DEP-11 64x64 Icons [64.2 kB]
Fetched 4,916 kB in 1s (2,680 kB/s)                                
Reading package lists... Done
Building dependency tree       
Reading state information... Done
26 packages can be upgraded. Run 'apt list --upgradable' to see them.
Reading package lists... Done
Building dependency tree       
Reading state information... Done
The following NEW packages will be installed:
  google-drive-ocamlfuse
0 upgraded, 1 newly installed, 0 to remove and 26 not upgraded.
Need to get 904 kB of archives.
After this operation, 3,978 kB of additional disk space will be used.
Get:1 http://ppa.launchpad.net/alessandro-strada/ppa/ubuntu xenial/main amd64 google-drive-ocamlfuse amd64 0.6.21-0ubuntu1~ubuntu16.04.1 [904 kB]
Fetched 904 kB in 1s (650 kB/s)                 
Selecting previously unselected package google-drive-ocamlfuse.
(Reading database ... 253806 files and directories currently installed.)
Preparing to unpack .../google-drive-ocamlfuse_0.6.21-0ubuntu1~ubuntu16.04.1_amd64.deb ...
Unpacking google-drive-ocamlfuse (0.6.21-0ubuntu1~ubuntu16.04.1) ...
Processing triggers for man-db (2.7.5-1) ...
Setting up google-drive-ocamlfuse (0.6.21-0ubuntu1~ubuntu16.04.1) ...
```

### 2. Get Client ID and Secret from Google Drive API

If you try to run `google-drive-ocamlfuse` on a headless machine that has no
`$DISPLAY` variable, you'll get an error.

```
utility@ds06:~$ google-drive-ocamlfuse
/usr/bin/xdg-open: line 771: www-browser: command not found
/usr/bin/xdg-open: line 771: links2: command not found
/usr/bin/xdg-open: line 771: elinks: command not found
/usr/bin/xdg-open: line 771: links: command not found
/usr/bin/xdg-open: line 771: lynx: command not found
/usr/bin/xdg-open: line 771: w3m: command not found
xdg-open: no method available for opening 'https://accounts.google.com/o/oauth2/auth?REDACTED'
Error: GDK_BACKEND does not match available displays
/bin/sh: google-chrome: command not found
Couldn't get a file descriptor referring to the console
Cannot retrieve auth tokens.
Failure("Error opening URL:https://accounts.google.com/o/oauth2/auth?REDACTED")
```

If you run with `headless` then you need to specify the Client ID and Secret in
the command line:

```
utility@ds06:~$ google-drive-ocamlfuse ~/googledrive -headless
Error: In headless mode, you should specify a client id and a client secret
```

Follow the instructions
[here](https://developers.google.com/drive/v3/web/quickstart/python) to use the
wizard to create Google API credentials. I've copied them below. There's a
weird step where you're supposed to "Cancel" instead of press 'OK' so pay
attention!

1. Use [this wizard](https://console.developers.google.com/start/api?id=drive) to create or select a project in the Google Developers Console and automatically turn on the API. Click **Continue** , then **Go to credentials** .
2. On the **Add credentials to your project** page, click the **Cancel** button.
3. At the top of the page, select the **OAuth consent screen** tab. Select an **Email address** , enter a **Product name** if not already set, and click the **Save** button.
4. Select the **Credentials** tab, click the **Create credentials** button and select **OAuth client ID** .
5. Select the application type **Other** , enter the name "Drive API Quickstart", and click the **Create** button.
6. Click **OK** to dismiss the resulting dialog.
7. Click the file_download (Download JSON) button to the right of the client ID.
8. Move this file to your working directory and rename it `client_secret.json`.



### 3. Copy the downloaded JSON to the utility box

```
➜  dobby git:(master) scp ~/Downloads/client_secret_1234asdf.apps.googleusercontent.com.json utility@ds06:~/client_secret.json
client_secret_1234asdf.apps.googleusercontent.com.json                                   100%  441   558.6KB/s   00:00  
```

### 4. Activate the Google Drive API

Now you have the proper authorizations on the computer, but you haven't allowed
that key to use Google Drive specifically yet. If you tried to continue setting
up `google-drive-ocamlfuse` as per the instructions, it's likely you'll get an
error when you try to see the files: `ls: cannot access 'googledrive':
Input/output error`

```
utility@ds06:~$ ll
ls: cannot access 'googledrive': Input/output error
total 144
drwxr-xr-x 20 utility utility  4096 Aug 18 12:39 ./
drwxr-xr-x  5 root    root     4096 Aug  9 11:52 ../
drwxrwxr-x  2 utility utility  4096 Aug  9 14:16 .aws/
-rw-------  1 utility utility 14191 Aug 18 12:14 .bash_history
-rw-r--r--  1 utility utility   220 Aug  9 11:52 .bash_logout
-rw-r--r--  1 utility utility  3771 Aug  9 11:52 .bashrc
drwx------  7 utility utility  4096 Aug 12 13:11 .cache/
-rw-r--r--  1 utility utility   441 Aug 18 12:39 client_secret.json
drwxr-xr-x 10 utility utility  4096 Aug 13 12:57 .config/
drwx------  3 utility utility  4096 Aug  9 11:54 .dbus/
drwxrwxr-x  2 utility utility  4096 Aug  9 11:54 Desktop/
drwx------  3 utility utility  4096 Aug 14 17:40 .emacs.d/
-rw-r--r--  1 utility utility  8980 Aug  9 11:52 examples.desktop
drwx------  2 utility utility  4096 Aug  9 12:30 .gconf/
drwx------  3 utility utility  4096 Aug 18 12:20 .gdfuse/
drwx------  3 utility utility  4096 Aug  9 12:29 .gnupg/
d?????????  ? ?       ?           ?            ? googledrive/
-rw-------  1 utility utility   362 Aug  9 12:29 .ICEauthority
drwxrwxr-x  5 utility utility  4096 Aug 12 13:12 .local/
drwx------  3 utility utility  4096 Aug 18 12:20 .mozilla/
drwxrwxr-x  2 utility utility  4096 Aug 12 13:56 .nano/
-rw-r--r--  1 utility utility   655 Aug  9 11:52 .profile
-rw-rw-r--  1 utility utility    66 Aug 12 13:56 .selected_editor
drwxrwxr-x  2 utility utility  4096 Aug 14 17:44 setup_stuff/
drwxrwxr-x  2 utility utility  4096 Aug 16 10:45 .ssh/
-rw-r--r--  1 utility utility     0 Aug  9 14:12 .sudo_as_admin_successful
drwxrwxr-x  2 utility utility  4096 Aug 16 12:30 testing_dir/
-rw-------  1 utility utility   720 Aug 10 11:43 .viminfo
drwx------  2 utility utility  4096 Aug  9 11:54 .vnc/
-rw-rw-r--  1 utility utility   895 Aug 18 12:00 watch_flexo.log
-rw-r--r--  1 utility utility  1600 Aug  9 11:52 .Xdefaults
-rw-r--r--  1 utility utility    14 Aug  9 11:52 .xscreensaver
-rw-------  1 utility utility     0 Aug  9 12:27 .xsession-errors
```

1. Go back to the
   [Google Developers API Console](https://console.developers.google.com/apis/library)
2. Click "Library"
3. Search for "Google Drive"
4. Click "Enable"


### 4. Mount the Google Drive folder!


Use your Client ID and Secret to authenticate in `-headless` mode for `google-drive-ocamlfuse`:

```
google-drive-ocamlfuse ~/googledrive -headless -id 1234-asdf.apps.googleusercontent.com -secret asdfasdfasdf
```