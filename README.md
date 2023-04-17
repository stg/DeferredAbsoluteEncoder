Deferred Absolute Position Encoder
==================================

This is based on an idea that struck me many years ago, when I needed to home a rig without much movement.  
I'm sure it is not novel, but I haven't seen it anywhere and I think it could be useful, so I wrote it up for posterity here.
Note that this is just a quick synopsis of the concept. The concept is not fully fleshed out and the code may not be perfectly efficient or bug-free.  

![First Produced Disc](./media/first_encoder.jpg?raw=true "First Produced Disc")

LFSRs are interesting, and one of their properties is that that the data shifted out of one will never show repetition across *N* bits (where *N* is the size of the shift register and referenced as such in the remainder of this document) until, of course, the LFSR cycle repeats after *2<sup>N-1</sup> steps.

This means that knowing any N bits means you can figure out exactly where in the sequence these *N* bits fit, much like a puzzle piece.

![6-Bit LFSR Puzzle](./media/puzzle.png?raw=true "6-Bit LFSR Puzzle")

To produce a sequence of *2<sup>N</sup>, which is preferable, you simply start with an initial value of 1 for the shift-register and prefix (or suffix) the sequence with a single 0.

Now, encoders typically come in two traditional flavors: **incremental** and **absolute**.  

**Incremental** encoders use a pair of quadrature signals to determine how many steps are produced, and in what direction.  

**Absolute** encoders typically use gray-coding (GC) and one signal per bit of resolution, making them more mecahnically complex to construct.  

We propose a third variant that is not immediately absolute but becomes absolute after a partial rotation of *360°×N/2<sup>N</sup>* degrees, termed the *indexing angle*. This variant requires only one additional signal in addition to the traditional incremental encoder and matches the commonly available and standard incremental-with-index-pulse encoder in construction. The extra track and signal (termed *Q*) is generated from a suitable LFSR stream wrapped around the disc and shifted 45° relative the A/B signals (either when generating the disc, or by sensor positioning).

![6-Bit/64-CPR Disc Variants](./media/variants.png?raw=true "6-Bit/64-CPR Disc Variants")

When a quadrature flank *A* or *B* is detected, one bit is read off *Q* and stored in an *N*-bit register at a position depending on the decoded quadrature signals. Once this register is filled, a lookup table (or reverse LFSR calculation) is used to determine the position at which these bits were read. Once this process is completed, absolute positioning is aquired and normal quadrature counting can be applied to maintain absolute positioning. Further *Q* extraction can be performed to verify or correct the positioning over time, providing error correction when desired.

An example (in Python) for generating discs is provided by [generator.py](./generator.py).  
Set your parameters (polynomial, which also controls register size, and desired radii) in the source code and run the program which will generate and preview the disc, and let you export an **SVG**-file and the corresponding **LUT** as an array in a C-file.  
  
An example (in C) for reading discs is provided in the [TeensyReader](./TeensyReader/) directory.  
The example is designed for Teensy3.2, but can of course be adapted for other suitable processors or hardware implementations.  

Sample discs and data is provided in the [examples](./examples/) directory.  

Further, this concept can be expanded upon to do linear deferred absolute positioning, or to add additional *Q* tracks with the advantage of decreasing the *indexing angle* but also with the disadvantage of requiring additional sensors. This opens up an opportunity to "tune" the performance depending on requirements.  
