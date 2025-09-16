Вариант 26.
<h3>Stage 1</h3>
Here's the work demonstration of the first stage of my VFS assignment which I'm required to upload publicly<br>

![screenshot](/demo_screenshots/stage_1.png?raw=true)<br>

I also implemented the "exit" command, but the window closes right after executing it, so there won't be much left to screenshot

<h3>Stage 2</h3>
I've implemented the following new features: accepting user-inputted parameters on startup for more flexibility, automated execution of a certain sequence of commands at every launch (starting script), and also the service command "config-dump" which outputs all user-inputted parameters.<br>
To conveniently put it all to the test, I've created 2 .bat scripts that start the VFS with different parameters.

First testing script displays the new functionality as well as proves that VFS stops executing the script right after catching an error: 
![screenshot](/demo_screenshots/stage_2.1.png?raw=true)<br>
![screenshot](/demo_screenshots/stage_2.2.png?raw=true)<br>
![screenshot](/demo_screenshots/stage_2.3.png?raw=true)<br>

Second testing script shows that the VFS doesn't break even if user inputs invalid parameters:
![screenshot](/demo_screenshots/stage_2.4.png?raw=true)<br>
![screenshot](/demo_screenshots/stage_2.5.png?raw=true)<br>