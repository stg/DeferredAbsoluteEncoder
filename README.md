Partially Absolute Encoder (Optical Wheels)
===========================================

This is based on an idea that struck me many years ago, when I needed to home a rig without much movement.  
I'm sure it is not novel, but I haven't seen it anywhere and I think it could be usedful so I wrote it up for public use here.
Note that this is just a quick writeup of the concept and the code may not be perfectly efficient or bug-free.  

![First Produced Wheel](./media/first_encoder.jpg?raw=true "First Produced Wheel")

LFSRs are interesting and one of their properties is that that the data shifted out of one will never show repetition across *N* bits (where *N* is the size of the shift register) until, of course, the LFSR cycle repeats after *2<sup>N-1</sup> steps.

This means that knowing any N bits means you can figure out exactly where in the sequence these *N* bits fit, much like a puzzle piece.

![6-Bit LFSR Puzzle](./media/puzzle.png?raw=true "6-Bit LFSR Puzzle")

Now, encoders typically come in two traditional flavors: **incremental** and **absolute**.  

**Incremental** encoders use a pair of quadrature signals to determine how many steps are produced, and it what direction.  

**Absolute** encoders typically use one gray-coding and one signal per bit of resolution, making them much more complex.  

We propose a third variant that is not immediately absolute but becomes absolute after a partial rotation of *360°/(N/(2<sup>N</sup>))* where *N* is the number of bits used. This variant requires only one additional signal in addition to the traditional quadrature incremental encoder. The extra track and signal *Q* is generated from a suitable LFSR stream wrapped around the disk and shifted 45° relative the A/B signals, either when generating the disk or by sensor positioning.

![6-Bit/64-CPR Wheel Variants](./media/variants.png?raw=true "6-Bit/64-CPR Wheel Variants")

When a quadrature flank *A or B* is detected, one bit is read off *Q* and stored in a register, depending on the direction of travel determined by the quadrature signals. Once this register contains *N* bits, a lookup table is used to determine the position at which these bits were read. Once this process is completed, absolute positioning is aquired and normal quadrature counting can be applied to maintain absolute positioning - or further *Q* extraction can be performed to verify or correct the positioning over time, if desired.

An example (in Python) for generating disks is provided by [generator.py](./generator.py).  
Set your parameters in the source code and run the program, which will preview the disk and let you export an **SVG**-file and a **LUT** as an array in a C-file.  
  
An example (in C) for reading disks is provided in the [TeensyReader](./TeensyReader/) directory.  
The example is designed for Teensy3.2, but can of course be adapted for other controllers.  

Sample disks and data is provided in the [examples](./examples/) directory.
