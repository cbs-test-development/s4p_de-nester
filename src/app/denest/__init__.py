"""Flatten nested S4P files into one folder and write a filtered leg map.

The feature is split by responsibility:

* :mod:`app.denest.naming` - building safe, unique destination filenames.
* :mod:`app.denest.legmap` - reading the leg map CSV and writing the filtered copy.
* :mod:`app.denest.discovery` - finding S4P files and matching them to serials.
* :mod:`app.denest.job` - planning and running a whole de-nest job.
* :mod:`app.denest.gui` - the Tkinter front end.

See ``docs/denest/README.md`` for the behaviour in full.
"""
