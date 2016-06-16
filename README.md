# Audio XBlock

A simple XBlock for playing audio files using the native HTML5 `<audio>` tag.

# Features

- Supports multiple sources. (We will interpret the audio MIME type based on the file extension, which lets the browser more easily figure out which source it supports)
- Supports displaying a link to download the audio file. (Configurable per XBlock instance, will use first source in sources list)

## Installation

Install the requirements into the Python virtual environment of your `edx-platform` installation by running the following command from the root folder:

```bash
$ pip install -r requirements.txt
```

## Enabling in Studio

You can enable the XBlock in Studio through `Advanced Settings`.

1. From the main page of a specific course, navigate to `Settings -> Advanced Settings` from the top menu.
2. Check for the `advanced_modules` policy key, and add `"audio"` to the policy value list.
3. Click the "Save changes" button.
