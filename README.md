# Gen AI Survey Bot, Recurring Themes and Sentiment Analysis

A Flask application that integrates with Google Generative AI to process user inputs and generate data visualizations.

## Prerequisites

- Python 3.12 (tested on, may work with older versions)
- Google Generative AI API Key

## Installation

1. Clone the repository and navigate to the project directory

```bash
git clone https://github.com/danielnzlz01/GenAIChatbot.git
```

```bash
cd GenAIChatbot
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r src/req.txt
```

4. Set up environment variables

```bash
export GOOGLE_API_KEY=your_api_key
```

5. Create and set up `uploads` directory for file uploads

```bash 
mkdir uploads
```

**Important** In your browser, set download location to `src/uploads` for audio functionality to work.

## Modifications 

- Extended `start_chat` method: Added a `temperature` parameter to allow customization of the temperature setting for chat sessions. Edit the `start_chat` method in `/lib/python3.x.x/site-packages/google/generativeai/generative_models.py` as follows:

```python
def start_chat(
        self,
        *,
        history: Iterable[content_types.StrictContentType] | None = None,
        enable_automatic_function_calling: bool = False,
        temperature: float | None = None,
    ) -> ChatSession:
        """Returns a `genai.ChatSession` attached to this model.

        >>> model = genai.GenerativeModel()
        >>> chat = model.start_chat(history=[...], temperature=0.7)
        >>> response = chat.send_message("Hello?")

        Arguments:
            history: An iterable of `protos.Content` objects, or equivalents to initialize the session.
            temperature: The temperature setting for the chat session.
        """
        if self._generation_config.get("candidate_count", 1) > 1:
            raise ValueError(
                "Invalid configuration: The chat functionality does not support `candidate_count` greater than 1."
            )

        if temperature is not None:
            self._generation_config["temperature"] = temperature

        return ChatSession(
            model=self,
            history=history,
            enable_automatic_function_calling=enable_automatic_function_calling,
        )
```

## Usage

1. Run the application

```bash
python src/chat.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. After survey completion, run the analysis script

```bash
python src/data_profile.py
```

## Notes

- Wordclouds can be a hit or miss depending on the data as they only display the most frequent words so if the recurring themes are in multiple words, they may not be displayed correctly.

## Future Work

- Deploy the application to a cloud service and integrate with a database to store multiple survey results.
- Implement a specialized model for recurring theme and sentiment analysis extraction.
- Implement better data visualization techniques.

## License

This project is licensed under the GNU GPLv3 - see the [COPYING](COPYING) file for details.

