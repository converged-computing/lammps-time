# Analysis Example

These are two logs generated from the same executable, so the paths accessed should be the same. In this directory I want to:

1. Calculate Levenstein Distance (see below)
2. Try to visualize the access
3. Try to create features to describe the pattern (specifically, the file lookup over time, not accounting for timestamps)
4. Then - can we do a total calculation of the percentage of files looked up over the total in the image?

For the last point - can we break files into groups based on access time, package that with metadata, and have that used for a pre-fetch strategy? Where groups are fetched before needed for an application?

## Usage

Calculate distance between the two:

```bash
python analyze-recording.py fs-record.log1176518852 fs-record.log631635294
```
```console
                        fs-record.log1176518852 fs-record.log631635294
fs-record.log1176518852                       0                      0
fs-record.log631635294                        0                      0
```

Visualize the access - a basic plot of the paths, and then make opacity based on access rate.
