# GSR Signal Decomposition Scripts.
Most of the signal decomposition for this is handled by one line of python by using
the neurokit2 library. As such --- there are some requirements needed to allow this to run.

### Requirements.
Should note - this code had only been tested by your main man Trev on a Ubuntu Linux
machine using Python3.6.9. You'll need at least Python3.6.1.

#### Installing requirements (Linux [probably Mac]):

Pop yourself in the root directory of the project and:

```
python3.{your_version_here} -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Installing requirements (Windoze [I hope]):

```
python3.{your_version_here} -m venv venv
source venv\Scripts\activate.bat
pip install -r requirements.txt
```

***If you care nothing for virtual environments then `pip install -r requirements.txt` will do you good.***

If neurokit2 gives you a pain when install requirements:

```
pip install neurokit2
```

### Yeah, but then what?

Basic usage is pretty standard for right now. Place all of the SHIMMER files you wish to
decompose into the create a directory called `./shimmer/` in the root directory,
add all the SHIMMER .csv files into that directory directory, and run:

`python NKShimmerDecompose.py`

If you don't feel like moving files around and just need to work with one file then
you can set the `data_fname` parameter in the decomposer when you call it. This should
force the decomposer to just run on the one file. You can also adjust the optional
parameters in the class to point to the directory where those files live.

### Okay, but where's the data?

The decomposed data should be placed into `./exports/`. Images will be placed into
`./exports/imgs`. You can set those arguments to be different if you're into that
sort of thing. See the docstring in `NKShimmerDecomposer.py` for more info about
the various options.
