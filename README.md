# Gen AI Survey Bot, Recurring Themes and Sentiment Analysis

A Flask application that integrates with Google Generative AI to process user inputs and generate data visualizations.

## Prerequisites

- Python 3.12 (tested on, may work with older versions)
- Google Generative AI API Key

## Installation

1. Clone the repository

```bash
git clone https://github.com/danielnzlz01/GenAIChatbot.git
```

2. Install dependencies

```bash
pip install -r /src/requirements.txt
```

3. Set up environment variables

```bash
export GOOGLE_API_KEY=your_api_key
```

## Usage

1. Run the application

```bash
python src/chat.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. After survey completion, run the analysis script

```bash
python src/data_profiling.py
```

## Notes

- Ensure the `uploads` and `data` directories exists; the scripts will create them if they don't.

## License

This project is licensed under the GNU GPLv3 - see the [LICENSE](LICENSE) file for details.

