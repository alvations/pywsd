Informal Benchmarks
=====

This file contains informal benchmark to make some decisions.


Making `from_cache` the default for Lesk based algorithms
====

The `from_cache` feature in `pywsd==1.1.7` will be the default because it's ~295 times faster than `from_cache=False`: 

```
~/git-stuff/pywsd$ python3 test_lesk_speed.py 
Warming up PyWSD (takes ~10 secs)... took 7.105613946914673 secs.
======== TESTING all-words lesk (`from_cache=True`)===========
Disambiguating 100 brown sentences took 0.7550220489501953 secs
======== TESTING all-words lesk (`from_cache=False`)===========
Disambiguating 10 brown sentences took 22.26057481765747 secs
```

**Note:** 2.226 / (0.75 / 100) = 284.83
