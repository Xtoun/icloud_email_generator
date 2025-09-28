<p align="center"><img width=60% src="docs/header.png"></p>

> Automated generation of Apple's iCloud emails via HideMyEmail.

_You do need to have an active iCloud+ subscription to be able to generate iCloud emails..._

<p align="center"><img src="docs/example.png"></p>

## Usage


Apple allows you to create 5 emails per hour. From my experience, they cap the total amount of iCloud emails you can generate at 750.

## Setup
> Python 3.12+ is required!

1. Clone this repository

```bash
git clone https://github.com/Xtoun/icloud_email_generator.git
cd icloud_email_generator
```

2. Install requirements

**Using virtual environment (recommended):**

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**On Ubuntu/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**Without virtual environment:**
```bash
pip install -r requirements.txt
```

3. [Save your cookie string](https://github.com/Xtoun/icloud_email_generator#getting-icloud-cookie-string)

   > You only need to do this once 🙂

4. You can now run the gen with:

**If using virtual environment, make sure to activate it first:**

**On Windows:**
```bash
# Activate virtual environment (if not already activated)
venv\Scripts\activate

# Run the script
python main.py
```

**On Ubuntu/Linux:**
```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Run the script
python3 main.py
```

**On Mac (without virtual environment):**

```bash
python3 main.py
```

**On Windows (without virtual environment):**

```bash
python main.py
```

## Getting iCloud cookie string

> There is more than one way how you can get the required cookie string but this one is _imo_ the simplest...

1. Download [EditThisCookie](https://chromewebstore.google.com/detail/editthiscookie-v3/ojfebgpkimhlhcblbalbfjblapadhbol) Chrome extension

2. Go to [EditThisCookie settings page](chrome-extension://ojfebgpkimhlhcblbalbfjblapadhbol/options_pages/user_preferences.html) and set the preferred export format to `Semicolon separated name=value pairs`

<p align="center"><img src="docs/cookie-settings.png" width=70%></p>

3. Navigate to [iCloud settings](https://www.icloud.com/settings/) in your browser and log in

4. Click on the EditThisCookie extension and export cookies

<p align="center"><img src="docs/export-cookies.png" width=70%></p>

5. Paste the exported cookies into a file named `cookie.txt`

# License

Licensed under the MIT License - see the [LICENSE file](./LICENSE) for more details.

Credit goes to **[rtuna](https://twitter.com/rtunazzz)**.
