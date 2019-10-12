Preprocessed Cassini Metadata

This repository contains parsed metadata for all of the images in the
[Cassini ISS Online Data
Volumes](https://pds-imaging.jpl.nasa.gov/volumes/iss.html). This
makes it possible to analyze the metadata surrounding the Cassini
missing images without downloading hundreds of gigabytes of actual
imagery.

Each volume of the original dataset is given its own newline-delimited
JSON file. The field names are the keywords described in the [ISS Data
User's
Guide](https://pds-rings.seti.org/cassini/iss/ISS_Data_User_Guide_120703.pdf).

The overall approach was inspired by John Keegan's
[cassini-tools](https://github.com/jonkeegan/cassini-tools), but the
code is original.
