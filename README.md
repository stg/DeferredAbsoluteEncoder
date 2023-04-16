Partially absolute (optical) encoder (wheels) based on LFSR data channel
========================================================================

This is based on an old idea of mine. I don't think it is novel, but I haven't seen it anywhere and I think it could be usedful so I wrote it up for public use here.

LFSRs are interesting and one property they have is that the data shifted out will never show repetition across N (where N is the size of the shift register) bits until, of course, the cycle repeats.

This means that knowing any N bits means you can figure out exactly where in the sequence these bits fit.
