FireSim
=======

FireSim is a GUI for designing lighting installations using addressable LED strips.
It can display the output of FireMix, which is useful for developing presets without hardware.

More information on preset development is on the [FireMix Page](https://github.com/craftyjon/firemix/)

![FireSim screenshot](/firesim.png?raw=true)


Installation / Development
--------------------------

    pip install -r requirements.txt
    python firesim.py demo

Getting Started
---------------

FireMix stores information about the current lightshow design in a Scene file (as a JSON dictionary).  The scene
can have a background image assigned (for reference when designing the show) and contains zero or more fixtures.
Each fixture is a set of individually-addressable RGB LEDs arranged in a 1xN grid (i.e. each fixture represents
a segment of a strip of RGB LEDs).  Pixels are addressed by a tuple of (strand, fixture, pixel), where each strand
represents an individual hardware controller, each fixture is a zero-based address along the strand, and each pixel
is a zero-based offset along a fixture.  Fixtures can have any number of pixels, and strands can have any number of
fixtures (in the simulator--in real life, you will be constrained by nuisances such as voltage droop and signal
integrity!)

When the scene is unlocked, you can use FireSim to design the lightshow.  Use the command buttons on the left to add
fixtures, and then drag them around with the mouse.  You can drag the control points on the end of the fixture, or the
entire fixture.  When a fixture is selected by left-clicking (highlighted in blue), you can edit its address and
number of pixels using the text boxes on the left.  To delete a fixture, middle-click on it twice (it will be highlighted
in red the first time to confirm deletion).

FireSim listens on UDP port 3020 for messages from FireMix.  At the moment, the network protocol has not been optimized
for use over an actual network, so performance will be best if both programs are running on the same machine.

Development is heavily focused on FireMix at the moment, so FireSim still has plenty of quirks.  Please report bugs
using the GitHub issue tracker if you find them, and feel free to submit pull requests with fixes or enhancements.
