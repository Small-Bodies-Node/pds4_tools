[1.4] - 2025-03-16
==================

Reader
------

**Added**

- Add `Label.iter` and `Label.itertext` methods

**Changed**

- Drop support for Python 2.6, 3.4 and 3.5
- Align docstring for `Label.to_dict(skip_attributes=...) <Label.to_dict>` parameter with its existing functionality

**Fixed**

- Compatibility with Python 3.12+, by updating vendored six to 1.17
- Compatibility with NumPy 2.0+
- Correct fill values for masked arrays having dtype of ``object``, previously broken after NumPy v1.24+
- Drop requirement for ``tkinter`` package when only reader is imported

Viewer
------

**Changed**

- Allow multiple LIDs in a single Local_Internal_Reference due to PDS4 Standards change

**Fixed**

- Compatibility with matplotlib 3.9+
- Do not raise exception for images where the display dictionary includes Movie_Display_Settings
- Fix data cube functionality of image display for 4+ dimensional arrays
- Ensure tkagg backend is still enforced with matplotlib 3.3+
- Fix exception in plot view related to grid visibility with matplotlib 3.7+


[1.3] - 2021-10-10
==================

Reader
------

**Added**

- Quiet keyword in `pds4_tools.read` will also accept log-level style values
- Added `pds4_tools.set_loglevel` function to control logging

**Changed**

- Allow line-feed as Table record delimiter due to PDS4 Standards change
- Recognize FITS 4.0 as plain-text header due to PDS4 Standards change
- Empty numeric values in Table_Delimited fields will have a default fill value
  of 0 instead of NumPy default
- Deprecated mask_numeric_nulls keyword in `data_type_convert_table_ascii`,
  use mask_nulls instead
- Propagation to ancestor loggers is off by default, see `pds4_tools.set_loglevel`

**Fixed**

- Table_Delimited read-in when ASCII_Boolean fields have empty values
- `PDSdtype` not-equal operator under Python2
- Default logger class will no longer be overwritten globally
- Deprecation warnings for aliases of built-in types under NumPy 1.20+

Viewer
------

**Added**

- Quiet keyword in ``pds4_tools.view`` will also accept log-level style values

**Fixed**

- Remove refresh-blinking on resize of image or plot with matplotlib 3.4+
- Deprecation warnings for cbook in matplotlib 3.4+


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
