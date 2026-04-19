---
title: Running the PreSonus Quantum interfaces on Windows 7
layout: post
image:
  feature: quantum.png
doi: "https://doi.org/10.59348/4ajge-gmj03"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2019/04/26/running-the-presonus-quantum-interfaces-on-windows-7"
---
The PreSonus Quantum interfaces are [definitely not supported on Windows 7](https://support.presonus.com/hc/en-us/articles/115003181806-Will-Quantum-work-with-my-Windows-10-machine-). But if you are not faint of heart, it is possible to hack the driver onto a Windows 7 system (or perhaps Windows 8). Here's how I did it.

OK, so first things first, this is TOTALLY unofficial, definitely not officially supported, and I am _not_ responsible if these instructions brick your Quantum, render your PC unbootable, or cause any other kind of damage. I'm also unlikely to respond to requests for suppport by email or any other means; it's all at your own risk and you should have some rudimentary understanding of what you are doing. You will probably void any warranty from PreSonus by following these instructions. Again, not my fault if you do. You also need a working Thunderbolt setup before you begin. If Thunderbolt isn't working for devices that are _supported_ on Windows 7, this certainly won't help you.

Steps:

1. Download the [files you need](/images/quantum_drivers.zip).
2. Install the default Universal Control application having dowloaded it from PreSonus (you'll note that, on Windows 7, you are _not_ given the option to install the Quantum Thunderbolt driver).
3. Put the "Quantum" folder inside my "Quantum_driver.zip" in "c:\Program Files\PreSonus\Universal Control\Drivers\". Check that you've done this right by verifying that c:\Program Files\PreSonus\Universal Control\Drivers\Quantum\x64\quantum_asio_x64.dll exists.
4. Go into Device Manager and update the driver for the (currently malfunctioning) Quantum device by pointing Windows at the c:\Program Files\PreSonus\Universal Control\Drivers\Quantum\x64\ directory.
5. Launch Universal Control. The Quantum device should be visible.
6. Update the firmware. This may crash mid-way through and a "U" will be displayed on the Quantum screen. If so, wait five minutes, then power the Quantum off. Unplug it. Unplug the Thunderbolt cable. Then plug it all back in 30 seconds later and power back on.
7. Launch regedit and import the two registry entries in the zip file.
8. Launch Universal Control and verify that you can connect.
9. Launch your DAW and select the Quantum device. 

Tada!




