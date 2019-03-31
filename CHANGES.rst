[1.2-dev]

...

[1.1] - 2018-03-30
==================

Reader
------

**Added**

- `PDSdtype` class, returned by new methods `Meta_ArrayStructure.data_type` and
  `Meta_Field.data_type`. Allows easier high-level comparison of PDS4 data types.
- `data_type_convert_dates` function, which allows converting dates in PDS4 fields
  from string into datetimes.

**Changed**

- `mask_special_constants` will check non-numeric matches after stripping
  leading/trailing whitespace in both constant value and input data. The PDS4
  standard is ambiguous on the proper matching method.
- Improved memory efficiency of `ArrayStructure.as_masked` and `TableStructure.as_masked`
- `download_file` will use Certifi as CA bundle when available

**Fixed**

- TableDelimited length calculation that could lead to MemoryError
- Invalid escape sequence deprecation warnings under Python 3.6+
- ElementTree deprecation warnings related to Python 2.6 support

Viewer
------

**Added**

- Manual aspect ratio adjustment in Image View
- Plotting of Date fields
- View menu in Plot View and Header View

**Changed**

- Generic arrays will no longer default to preserving aspect ratio when the difference
  is 1:20 or greater.
- Image View will default to automatically ignoring Special_Constants when scaling
- Table View will ignore field_format for scaled/offset values since PDS4 Standard
  is ambiguous whether this format is before or after scaling
- Fields containing bit strings will be shown as hexadecimal byte values in Table View
- Fields containing bit strings will be exported as hexadecimal byte values
- Plots showing only points will default to auto limits rather than tight limits

**Fixed**

- Grayscale display for individual bands in RGB images
- Rare cases where zscale would raise an exception
- Plotting of masked fields against row number
- Tick label font options in Plot View
- Compatibility with matplotlib 2.2+ and 3.0
- Compatibility with OSX 10.14


[1.0] - 2018-08-11
==================

First stable release.
