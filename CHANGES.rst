[1.2] - 2020-10-04
==================

Reader
------

**Changed**

- `Label.to_string` will preserve trailing whitespace in multi-line strings
- `download_file` will fall back to system certificates if Certifi is available and fails

**Fixed**

- TableDelimited read-in when using semi-colon delimiter
- Array read-in when label contains an empty Object_Statistics
- `StructureList.__getitem__` can still retrieve by name when LID is present
- `ArrayStructure.as_masked` will work when data has no masked values
- `data_type_convert_dates` will work for datetimes with fractional seconds
- `Label.to_string` will pretty print empty elements
- URLOpen deprecation warnings for cafile under Python 3.6+

Viewer
------

**Added**

- Added 'Identification Area', 'Observation Area' and 'File Area' to Label View -> View menu
- Following methods are now exposed: ``Window.get_window_title``, ``Window.set_window_title``,
  ``Window.set_window_geometry``, ``Window.show_window`` and ``Window.hide_window``.

**Changed**

- ``pds4_tools.view`` will warn when IPython is already initialized with non-TK backend

**Fixed**

- Hiding tick labels in Plot View
- Label View search after changing which label is shown via View menu
- SyntaxWarning in Plot View under Python 3.8+


[1.1] - 2019-03-30
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
